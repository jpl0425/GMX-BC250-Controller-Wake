cmake_minimum_required(VERSION 3.13)

# Build with:  -DPICO_BOARD=pico_w   (Raspberry Pi Pico W)
#         or:  -DPICO_BOARD=pico2_w  (Raspberry Pi Pico 2 W)
include(pico_sdk_import.cmake)

project(gmx_bc250_wake C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(gmx_bc250_wake
    src/main.c
)

target_include_directories(gmx_bc250_wake PRIVATE ${CMAKE_CURRENT_LIST_DIR}/src)

target_compile_definitions(gmx_bc250_wake PRIVATE
    PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=0
    CYW43_LWIP=0
)

target_link_libraries(gmx_bc250_wake
    pico_stdlib
    pico_cyw43_arch_poll
    pico_btstack_cyw43
    pico_btstack_ble
)

pico_enable_stdio_usb(gmx_bc250_wake 1)
pico_enable_stdio_uart(gmx_bc250_wake 0)
pico_add_extra_outputs(gmx_bc250_wake)
