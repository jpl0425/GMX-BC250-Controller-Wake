/*
 * GMX BC-250 Controller Wake  -  Rev 1
 * Grumblymanx Mods
 *
 * Firmware for Raspberry Pi Pico W / Pico 2 W.
 *
 * Turns on an AMD BC-250 PC when a saved Xbox Series X|S controller is
 * switched on. The Pico W listens (passive Bluetooth LE scan) for the
 * controller's broadcasts while the PC is off. When it hears a saved
 * controller it:
 *   1. switches the ATX power supply on (PS_ON wire, optional), waits 1 s
 *   2. "presses" the BC-250 power button for 0.5 s
 *   3. waits up to 20 s for the BC-250 "PC is on" signal (TPMS1 pin 9)
 * The controller is never connected to the Pico - it still pairs and connects
 * to the BC-250 itself, exactly as before.
 *
 * Method based on the ESP32 projects by dexikdex
 * (ESP32-BC250-LOP_PSU-PowerON-Xbox) and GreatApo (BC250_ESP32_ATX_PSU).
 *
 * Pins (Pico GPIO numbers):
 *   GP2  out  Power-button MOSFET gate  (HIGH = button pressed)
 *   GP3  out  PS_ON MOSFET gate         (HIGH = power supply ON)
 *   GP4  in   PC-on sense from BC-250 TPMS1 pin 9 (3.3 V = PC on)
 *   GP5  in   Optional push button to GND
 *   GP6  out  Optional status LED (copy of the on-board LED)
 *
 * Buttons (optional GP5 button, or the Pico's own BOOTSEL button):
 *   short press  (under 3 s)  GP5 only: PC off -> turn PC on,
 *                                       PC on  -> press BC-250 power button
 *   hold 5-10 s, then release : learn a controller (pairing mode)
 *   hold over 10 s, release   : forget all saved controllers
 */

#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/gpio.h"
#include "hardware/sync.h"
#include "hardware/structs/ioqspi.h"
#include "hardware/structs/sio.h"

#include "btstack.h"
#include "btstack_tlv.h"

#define FW_NAME     "GMX BC-250 Controller Wake"
#define FW_VERSION  "Rev1 (1.0.0)"

/* ---------------- pins ---------------- */
#define PIN_PWR_BTN   2
#define PIN_PS_ON     3
#define PIN_PC_SENSE  4
#define PIN_BUTTON    5
#define PIN_EXT_LED   6

/* ---------------- timings (ms) ---------------- */
#define PSU_SETTLE_MS            1000u   /* PS_ON on -> wait before button  */
#define BUTTON_PRESS_MS           500u   /* power-button pulse length       */
#define WAIT_FOR_PC_ON_MS       20000u   /* give up if PC not on by then    */
#define WAKE_COOLDOWN_MS        15000u   /* ignore controller after a wake  */
#define SHUTDOWN_IGNORE_MS      60000u   /* ignore controller after PC off  */
#define PSU_OFF_DELAY_MS        10000u   /* PC off this long -> PS_ON off   */
#define SENSE_DEBOUNCE_MS         100u
#define BOOT_IGNORE_MS           3000u   /* ignore controller right after boot */
#define LEARN_IGNORE_MS         30000u   /* ignore controllers after learn mode ends */

#define BTN_SHORT_MAX_MS         3000u
#define BTN_LEARN_MIN_MS         5000u
#define BTN_CLEAR_MIN_MS        10000u

#define LEARN_TIMEOUT_MS        30000u   /* learn mode gives up after this  */
#define LEARN_SETTLE_MS          3000u   /* collect candidates this long    */
#define LEARN_RSSI_NEAR          (-55)   /* "right next to the Pico"        */
#define LEARN_RSSI_XBOX_NAME     (-75)   /* if it says "Xbox", allow further */

/* ---------------- storage ---------------- */
#define MAX_CONTROLLERS 4
#define TLV_TAG(i) (((uint32_t)'G' << 24) | ((uint32_t)'M' << 16) | ((uint32_t)'X' << 8) | (uint32_t)(i))

typedef struct {
    uint8_t used;
    uint8_t addr_type;
    bd_addr_t addr;
} saved_ctrl_t;

static saved_ctrl_t saved[MAX_CONTROLLERS];

/* ---------------- state ---------------- */
typedef enum { WAKE_IDLE, WAKE_PSU_SETTLE, WAKE_PRESSING, WAKE_WAIT_ON } wake_state_t;

static wake_state_t wake_state = WAKE_IDLE;
static uint32_t     wake_t0;
static bool         wake_requested;
static uint32_t     last_wake_ms;
static bool         have_woken_once;

static bool     pc_on;                 /* debounced */
static bool     sense_raw_last;
static uint32_t sense_change_ms;
static uint32_t pc_off_since_ms;
static uint32_t last_shutdown_ms;
static bool     have_shutdown_once;

static bool     ps_on_active;
static bool     shutdown_press_active;
static uint32_t shutdown_press_t0;

static bool     hci_ready;
static bool     scanning;
static bool     scan_active_mode;

static bool     learning;
static uint32_t learn_t0;
static bool     learn_have_candidate;
static uint32_t learn_first_seen_ms;
static int      learn_best_score;
static bd_addr_t learn_best_addr;
static uint8_t  learn_best_type;
static int8_t   learn_best_rssi;
static bool     learn_best_is_xbox;
static uint32_t learn_end_ms;
static bool     have_learned_once;

/* LED pattern override */
typedef enum { LEDP_NONE, LEDP_SAVED, LEDP_CLEARED, LEDP_FAILED } led_pattern_t;
static led_pattern_t led_pattern = LEDP_NONE;
static uint32_t      led_pattern_t0;

static btstack_packet_callback_registration_t hci_cb;

static inline uint32_t now_ms(void) { return to_ms_since_boot(get_absolute_time()); }

/* ======================================================================= */
/*  BOOTSEL button read (from pico-examples/picoboard/button)              */
/* ======================================================================= */
static bool __no_inline_not_in_flash_func(get_bootsel_button)(void) {
    const uint CS_PIN_INDEX = 1;
    uint32_t flags = save_and_disable_interrupts();
    hw_write_masked(&ioqspi_hw->io[CS_PIN_INDEX].ctrl,
                    GPIO_OVERRIDE_LOW << IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_LSB,
                    IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);
    for (volatile int i = 0; i < 1000; ++i);
#if PICO_RP2040
#define CS_BIT (1u << 1)
#else
#define CS_BIT SIO_GPIO_HI_IN_QSPI_CSN_BITS
#endif
    bool pressed = !(sio_hw->gpio_hi_in & CS_BIT);
    hw_write_masked(&ioqspi_hw->io[CS_PIN_INDEX].ctrl,
                    GPIO_OVERRIDE_NORMAL << IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_LSB,
                    IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);
    restore_interrupts(flags);
    return pressed;
}

/* ======================================================================= */
/*  Outputs                                                                */
/* ======================================================================= */
static void set_ps_on(bool on) {
    if (on != ps_on_active) printf("[PSU] PS_ON %s\n", on ? "ON (supply on)" : "OFF (supply may switch off)");
    ps_on_active = on;
    gpio_put(PIN_PS_ON, on);
}

static void set_pwr_btn(bool pressed) { gpio_put(PIN_PWR_BTN, pressed); }

static void set_led(bool on) {
    static int last = -1;
    if (last == (int)on) return;            /* only talk to the radio chip when it changes */
    last = on;
    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, on);
    gpio_put(PIN_EXT_LED, on);
}

/* ======================================================================= */
/*  Saved controllers (flash, via BTstack TLV)                             */
/* ======================================================================= */
static int saved_count(void) {
    int n = 0;
    for (int i = 0; i < MAX_CONTROLLERS; i++) if (saved[i].used) n++;
    return n;
}

static void load_saved(void) {
    const btstack_tlv_t *tlv; void *ctx;
    btstack_tlv_get_instance(&tlv, &ctx);
    memset(saved, 0, sizeof(saved));
    if (!tlv) { printf("[MEM] no storage available\n"); return; }
    for (int i = 0; i < MAX_CONTROLLERS; i++) {
        saved_ctrl_t s;
        int n = tlv->get_tag(ctx, TLV_TAG(i), (uint8_t *)&s, sizeof(s));
        if (n == (int)sizeof(s) && s.used == 1) saved[i] = s;
    }
    printf("[MEM] %d saved controller(s)\n", saved_count());
    for (int i = 0; i < MAX_CONTROLLERS; i++)
        if (saved[i].used) printf("      slot %d: %s\n", i + 1, bd_addr_to_str(saved[i].addr));
}

static bool is_saved(const bd_addr_t a) {
    for (int i = 0; i < MAX_CONTROLLERS; i++)
        if (saved[i].used && bd_addr_cmp(saved[i].addr, a) == 0) return true;
    return false;
}

static void save_controller(const bd_addr_t a, uint8_t type) {
    const btstack_tlv_t *tlv; void *ctx;
    btstack_tlv_get_instance(&tlv, &ctx);
    if (is_saved(a)) { printf("[MEM] %s already saved\n", bd_addr_to_str(a)); return; }
    int slot = -1;
    for (int i = 0; i < MAX_CONTROLLERS; i++) if (!saved[i].used) { slot = i; break; }
    if (slot < 0) {   /* full: shift everything down, newest goes last */
        for (int i = 0; i < MAX_CONTROLLERS - 1; i++) saved[i] = saved[i + 1];
        slot = MAX_CONTROLLERS - 1;
        for (int i = 0; i < MAX_CONTROLLERS - 1; i++)
            if (tlv) tlv->store_tag(ctx, TLV_TAG(i), (const uint8_t *)&saved[i], sizeof(saved_ctrl_t));
    }
    saved[slot].used = 1;
    saved[slot].addr_type = type;
    bd_addr_copy(saved[slot].addr, a);
    if (tlv) tlv->store_tag(ctx, TLV_TAG(slot), (const uint8_t *)&saved[slot], sizeof(saved_ctrl_t));
    printf("[MEM] saved controller %s in slot %d\n", bd_addr_to_str(a), slot + 1);
}

static void clear_controllers(void) {
    const btstack_tlv_t *tlv; void *ctx;
    btstack_tlv_get_instance(&tlv, &ctx);
    for (int i = 0; i < MAX_CONTROLLERS; i++) if (tlv) tlv->delete_tag(ctx, TLV_TAG(i));
    memset(saved, 0, sizeof(saved));
    printf("[MEM] all saved controllers forgotten\n");
}

/* ======================================================================= */
/*  Bluetooth scanning                                                     */
/* ======================================================================= */
static void scan_update(void) {
    if (!hci_ready) return;
    bool want = learning || !pc_on;               /* listen only while PC is off (or learning) */
    bool want_active = learning;                  /* active scan asks for the device name */
    if (scanning && (!want || want_active != scan_active_mode)) {
        gap_stop_scan();
        scanning = false;
    }
    if (want && !scanning) {
        /* type, interval, window (units of 0.625 ms), filter policy 0 = accept all */
        gap_set_scan_params(want_active ? 1 : 0, 0x0060, 0x0060, 0);
        gap_start_scan();
        scanning = true;
        scan_active_mode = want_active;
        printf("[BT] scanning (%s)\n", want_active ? "learn mode" : "listening for saved controllers");
    }
}

static bool adv_name_has_xbox(const uint8_t *data, uint8_t len) {
    ad_context_t it;
    for (ad_iterator_init(&it, len, data); ad_iterator_has_more(&it); ad_iterator_next(&it)) {
        uint8_t t = ad_iterator_get_data_type(&it);
        if (t == BLUETOOTH_DATA_TYPE_COMPLETE_LOCAL_NAME || t == BLUETOOTH_DATA_TYPE_SHORTENED_LOCAL_NAME) {
            uint8_t n = ad_iterator_get_data_len(&it);
            const uint8_t *p = ad_iterator_get_data(&it);
            char name[33];
            if (n > 32) n = 32;
            memcpy(name, p, n); name[n] = 0;
            if (strstr(name, "Xbox") || strstr(name, "XBOX") || strstr(name, "xbox")) return true;
        }
    }
    return false;
}

static bool controller_wake_allowed(uint32_t t) {
    if (t < BOOT_IGNORE_MS) return false;
    if (pc_on) return false;
    if (wake_state != WAKE_IDLE || wake_requested) return false;
    if (have_woken_once && (t - last_wake_ms) < WAKE_COOLDOWN_MS) return false;
    if (have_shutdown_once && (t - last_shutdown_ms) < SHUTDOWN_IGNORE_MS) return false;
    if (have_learned_once && (t - learn_end_ms) < LEARN_IGNORE_MS) return false;
    return true;
}

static void handle_adv_report(const uint8_t *packet) {
    bd_addr_t addr;
    gap_event_advertising_report_get_address(packet, addr);
    uint8_t type = gap_event_advertising_report_get_address_type(packet);
    int8_t rssi  = (int8_t)gap_event_advertising_report_get_rssi(packet);
    uint8_t len  = gap_event_advertising_report_get_data_length(packet);
    const uint8_t *data = gap_event_advertising_report_get_data(packet);
    uint32_t t = now_ms();

    if (learning) {
        bool xbox = adv_name_has_xbox(data, len);
        bool qualifies = (rssi >= LEARN_RSSI_NEAR) || (xbox && rssi >= LEARN_RSSI_XBOX_NAME);
        if (!qualifies) return;
        int score = (xbox ? 1000 : 0) + rssi;
        if (!learn_have_candidate || score > learn_best_score) {
            if (!learn_have_candidate) learn_first_seen_ms = t;
            learn_have_candidate = true;
            learn_best_score = score;
            bd_addr_copy(learn_best_addr, addr);
            learn_best_type = type;
            learn_best_rssi = rssi;
            learn_best_is_xbox = xbox;
            printf("[LEARN] candidate %s  rssi %d dBm  %s\n", bd_addr_to_str(addr), rssi,
                   xbox ? "(name says Xbox)" : "");
        }
        return;
    }

    if (!is_saved(addr)) return;
    if (!controller_wake_allowed(t)) return;
    printf("[BT] saved controller %s heard (rssi %d dBm) -> turning PC on\n", bd_addr_to_str(addr), rssi);
    wake_requested = true;
}

static void hci_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
    UNUSED(channel); UNUSED(size);
    if (packet_type != HCI_EVENT_PACKET) return;
    switch (hci_event_packet_get_type(packet)) {
        case BTSTACK_EVENT_STATE:
            if (btstack_event_state_get_state(packet) == HCI_STATE_WORKING) {
                bd_addr_t local;
                gap_local_bd_addr(local);
                printf("[BT] Bluetooth ready, Pico address %s\n", bd_addr_to_str(local));
                hci_ready = true;
                load_saved();
                scanning = false;
                scan_update();
            } else {
                hci_ready = false;
                scanning = false;
            }
            break;
        case GAP_EVENT_ADVERTISING_REPORT:
            handle_adv_report(packet);
            break;
        default:
            break;
    }
}

/* ======================================================================= */
/*  Learn mode                                                             */
/* ======================================================================= */
static void learn_start(void) {
    learning = true;
    learn_t0 = now_ms();
    learn_have_candidate = false;
    learn_best_score = -100000;
    printf("[LEARN] learn mode ON - hold the controller right next to the Pico and switch it on\n");
    scan_update();
}

static void learn_finish(bool ok) {
    learning = false;
    learn_end_ms = now_ms(); have_learned_once = true;   /* don't wake from the controller we just learned */
    if (ok) {
        printf("[LEARN] chose %s (rssi %d dBm%s)\n", bd_addr_to_str(learn_best_addr), learn_best_rssi,
               learn_best_is_xbox ? ", name says Xbox" : "");
        save_controller(learn_best_addr, learn_best_type);
        led_pattern = LEDP_SAVED;
    } else {
        printf("[LEARN] nothing found - learn mode timed out\n");
        led_pattern = LEDP_FAILED;
    }
    led_pattern_t0 = now_ms();
    scan_update();
}

static void learn_poll(uint32_t t) {
    if (!learning) return;
    if (learn_have_candidate && (t - learn_first_seen_ms) >= LEARN_SETTLE_MS) learn_finish(true);
    else if ((t - learn_t0) >= LEARN_TIMEOUT_MS) learn_finish(false);
}

/* ======================================================================= */
/*  PC sense + power sequencing                                            */
/* ======================================================================= */
static void sense_poll(uint32_t t) {
    bool raw = gpio_get(PIN_PC_SENSE);
    if (raw != sense_raw_last) { sense_raw_last = raw; sense_change_ms = t; }
    if (raw != pc_on && (t - sense_change_ms) >= SENSE_DEBOUNCE_MS) {
        pc_on = raw;
        if (pc_on) {
            printf("[PC] BC-250 is ON\n");
            set_ps_on(true);            /* keep the supply on while running */
        } else {
            printf("[PC] BC-250 is OFF - ignoring controllers for %u s\n", SHUTDOWN_IGNORE_MS / 1000);
            last_shutdown_ms = t; have_shutdown_once = true;
            pc_off_since_ms = t;
        }
        scan_update();
    }
    /* release PS_ON once the PC has been off for a while (and nothing is in progress) */
    if (!pc_on && ps_on_active && wake_state == WAKE_IDLE && !shutdown_press_active &&
        (t - pc_off_since_ms) >= PSU_OFF_DELAY_MS) {
        set_ps_on(false);
    }
}

static void wake_poll(uint32_t t) {
    switch (wake_state) {
        case WAKE_IDLE:
            if (wake_requested) {
                wake_requested = false;
                if (pc_on) break;
                last_wake_ms = t; have_woken_once = true;
                printf("[WAKE] step 1: power supply on\n");
                set_ps_on(true);
                wake_state = WAKE_PSU_SETTLE; wake_t0 = t;
            }
            break;
        case WAKE_PSU_SETTLE:
            if ((t - wake_t0) >= PSU_SETTLE_MS) {
                printf("[WAKE] step 2: pressing BC-250 power button\n");
                set_pwr_btn(true);
                wake_state = WAKE_PRESSING; wake_t0 = t;
            }
            break;
        case WAKE_PRESSING:
            if ((t - wake_t0) >= BUTTON_PRESS_MS) {
                set_pwr_btn(false);
                printf("[WAKE] step 3: waiting for the PC-on signal\n");
                wake_state = WAKE_WAIT_ON; wake_t0 = t;
            }
            break;
        case WAKE_WAIT_ON:
            if (pc_on) {
                printf("[WAKE] done - PC is on\n");
                wake_state = WAKE_IDLE;
            } else if ((t - wake_t0) >= WAIT_FOR_PC_ON_MS) {
                printf("[WAKE] FAILED - no PC-on signal after %u s (check wiring / AUTO_PWRON1 jumper)\n",
                       WAIT_FOR_PC_ON_MS / 1000);
                pc_off_since_ms = t;        /* PS_ON released after PSU_OFF_DELAY_MS */
                wake_state = WAKE_IDLE;
                led_pattern = LEDP_FAILED; led_pattern_t0 = t;
            }
            break;
    }
    /* manual shutdown press (button short-press while PC is on) */
    if (shutdown_press_active && (t - shutdown_press_t0) >= BUTTON_PRESS_MS) {
        set_pwr_btn(false);
        shutdown_press_active = false;
    }
}

/* ======================================================================= */
/*  Buttons                                                                */
/* ======================================================================= */
static void handle_release(uint32_t held, bool is_gp5) {
    if (held >= BTN_CLEAR_MIN_MS) {
        if (learning) learning = false;
        clear_controllers();
        led_pattern = LEDP_CLEARED; led_pattern_t0 = now_ms();
        scan_update();
    } else if (held >= BTN_LEARN_MIN_MS) {
        learn_start();
    } else if (held >= 50 && held < BTN_SHORT_MAX_MS && is_gp5) {
        if (learning) { printf("[BTN] learn mode cancelled\n"); learning = false; scan_update(); return; }
        if (!pc_on) {
            printf("[BTN] button pressed -> turning PC on\n");
            if (wake_state == WAKE_IDLE) wake_requested = true;
        } else if (!shutdown_press_active) {
            printf("[BTN] button pressed -> pressing BC-250 power button (shutdown)\n");
            set_pwr_btn(true);
            shutdown_press_active = true; shutdown_press_t0 = now_ms();
        }
    }
}

static void buttons_poll(uint32_t t) {
    static bool gp5_down, boot_down;
    static uint32_t gp5_t0, boot_t0, gp5_last_ms, boot_last_ms;

    /* GP5 (active low, debounced by 20 ms sampling) */
    if ((t - gp5_last_ms) >= 20) {
        gp5_last_ms = t;
        bool down = !gpio_get(PIN_BUTTON);
        if (down && !gp5_down) { gp5_down = true; gp5_t0 = t; }
        else if (!down && gp5_down) { gp5_down = false; handle_release(t - gp5_t0, true); }
    }
    /* BOOTSEL (sampled every 50 ms) */
    if ((t - boot_last_ms) >= 50) {
        boot_last_ms = t;
        bool down = get_bootsel_button();
        if (down && !boot_down) { boot_down = true; boot_t0 = t; }
        else if (!down && boot_down) { boot_down = false; handle_release(t - boot_t0, false); }
    }
}

/* ======================================================================= */
/*  LED                                                                    */
/* ======================================================================= */
static void led_poll(uint32_t t) {
    bool on = false;
    if (led_pattern != LEDP_NONE) {
        uint32_t e = t - led_pattern_t0;
        switch (led_pattern) {
            case LEDP_SAVED:   /* 3 long blinks */
                if (e >= 3000) led_pattern = LEDP_NONE; else on = (e % 1000) < 500; break;
            case LEDP_CLEARED: /* 6 quick blinks */
                if (e >= 1800) led_pattern = LEDP_NONE; else on = (e % 300) < 150; break;
            case LEDP_FAILED:  /* one 2-second flash */
                if (e >= 2500) led_pattern = LEDP_NONE; else on = e < 2000; break;
            default: break;
        }
        if (led_pattern != LEDP_NONE) { set_led(on); return; }
    }
    if (learning)                   on = (t % 200) < 100;           /* fast blink   */
    else if (wake_state != WAKE_IDLE || pc_on) on = true;           /* solid        */
    else if (saved_count() == 0)    { uint32_t p = t % 2000; on = (p < 80) || (p >= 250 && p < 330); } /* double flash */
    else                            on = (t % 2000) < 60;           /* heartbeat    */
    set_led(on);
}

/* ======================================================================= */
/*  main                                                                   */
/* ======================================================================= */
int main(void) {
    /* Outputs first, driven LOW = MOSFETs off (nothing pressed, PS_ON untouched) */
    gpio_init(PIN_PWR_BTN); gpio_set_dir(PIN_PWR_BTN, GPIO_OUT); gpio_put(PIN_PWR_BTN, 0);
    gpio_init(PIN_PS_ON);   gpio_set_dir(PIN_PS_ON, GPIO_OUT);   gpio_put(PIN_PS_ON, 0);
    gpio_init(PIN_EXT_LED); gpio_set_dir(PIN_EXT_LED, GPIO_OUT); gpio_put(PIN_EXT_LED, 0);
    gpio_init(PIN_PC_SENSE); gpio_set_dir(PIN_PC_SENSE, GPIO_IN); gpio_pull_down(PIN_PC_SENSE);
    gpio_init(PIN_BUTTON);   gpio_set_dir(PIN_BUTTON, GPIO_IN);   gpio_pull_up(PIN_BUTTON);

    stdio_init_all();

    /* If the PC is already running when the Pico starts, keep the supply on */
    sleep_ms(20);
    pc_on = gpio_get(PIN_PC_SENSE);
    sense_raw_last = pc_on;
    if (pc_on) set_ps_on(true);

    if (cyw43_arch_init()) {
        printf("cyw43 init failed\n");
        while (true) { gpio_put(PIN_EXT_LED, 1); sleep_ms(100); gpio_put(PIN_EXT_LED, 0); sleep_ms(100); }
    }

    printf("\n%s  %s\n", FW_NAME, FW_VERSION);
    printf("PC is %s at start-up\n", pc_on ? "ON" : "OFF");

    hci_cb.callback = &hci_handler;
    hci_add_event_handler(&hci_cb);
    hci_power_control(HCI_POWER_ON);

    while (true) {
        cyw43_arch_poll();
        uint32_t t = now_ms();
        sense_poll(t);
        wake_poll(t);
        buttons_poll(t);
        learn_poll(t);
        led_poll(t);
        cyw43_arch_wait_for_work_until(make_timeout_time_ms(5));
    }
}
