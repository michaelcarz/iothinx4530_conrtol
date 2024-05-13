from ioThinx_4530 import ioThinx_4530_API
import time
import threading

def handle_input(do_values, manual_override, device):
    # 處理用戶輸入的線程函數
    while True:
        print("輸入 'DO' 加通道號碼 (0-6) 切換，或輸入 'q' 退出: \n", end="")
        key_input = input().lower()  # 獲取並轉換為小寫的輸入
        if key_input == 'q':  # 如果輸入為'q'，則退出
            global running
            running = False  # 設置標誌，以便主循環可以退出
            break
        elif key_input.startswith('do'):
            _, channel_str = key_input.split()
            if channel_str.isdigit():
                channel = int(channel_str)
                if 0 <= channel < len(do_values):
                    do_values[channel] = 1 - do_values[channel]  # 切換DO的狀態
                    manual_override[channel] = True  # 標記為手動覆蓋
                    print("DO[%d] toggled to %d" % (channel, do_values[channel]))
                    device.ioThinx_DO_SetValues(1, do_values)
                else:
                    print("通道號碼無效。請輸入有效的號碼。")
            else:
                print("輸入格式無效。請使用 'DO#' 格式。")

def main():
    global running
    running = True  # 控制程式運行的全局變量

    slot = 1  # 使用的槽位
    do_count = 7  # DO通道數量
    di_count = 7  # DI通道數量
    do_values = [0] * do_count  # DO的狀態初始化為0
    manual_override = [False] * do_count  # 初始化手動覆蓋狀態為False
    di_filter = [2] * di_count  # 為DI通道設置過濾器

    # 初始化ioThinx I/O
    device = ioThinx_4530_API.ioThinx_4530_API()
    device.ioThinx_DO_Config_SetModes(slot, 0, do_count, [0] * do_count)
    device.ioThinx_DI_Config_SetFilters(slot, 0, di_count, di_filter)
    device.ioThinx_IO_Config_Reload()

    last_di_values = None  # 用於追蹤上一次DI值的變量

    # 啟動處理用戶輸入的線程
    input_thread = threading.Thread(target=handle_input, args=(do_values, manual_override, device))
    input_thread.start()

    try:
        while running:
            di_values = device.ioThinx_DI_GetValues(slot)  # 讀取DI的當前值
            # 僅在DI值改變時才輸出
            if di_values != last_di_values:
                print("Current DI values:\n", di_values)  # 打印DI值
                last_di_values = di_values

            # 根據DI值更新DO，除非被手動覆蓋
            for i in range(di_count):
                if not manual_override[i]:
                    do_values[i] = di_values[i]

            # 更新DO狀態
            device.ioThinx_DO_SetValues(slot, do_values)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("程式終止。")  # 捕捉到中斷信號，程式終止
    finally:
        # 在程式終止前，重置所有DO燈號
        do_values = [0] * do_count
        device.ioThinx_DO_SetValues(slot, do_values)
        print("所有 DO 燈號已關閉。")

if __name__ == '__main__':
    main()
