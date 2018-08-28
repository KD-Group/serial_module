# serial_module:串行接口模块
## 目录结构:
* doc
    * KDA自动换挡通讯协议V1.0.1.doc: 上位机(电脑软件)与单片机通讯协议
* serial_mod
    * base
        * mock_serial.py: 模拟通讯串行接口基类
        * real_serial.py: 真实通讯串行接口基类
        * serial_debug.py: 用于实现debug对关键变量的输出
    * controller
        * KDA_serial_controller.py: KDA项目所需的串行接口控制类
        * ...... 其它项目如有需要串行接口控制类,可放在该目录
    * data_type
        * hex_struct.py: 十六进制结构体,主要用于将其它类型转为bytes,便于写入串行接口
        * ...... 如有其它类型的定义,可放在该目录
    * exception
        * connection_exception.py: 连接异常(没有插上专用串行接口或通讯协议错误导致)
        * not_connected_exception.py: 无连接异常(用户需要自动手动调用函数连接)
        * probe_not_down_exception.py: 探头无下压异常
        * respond_parse_exception.py: 单片机的返回数据解析异常(crc8校验失败/与通讯协议不对应)
        * timeout_exception.py: 超时异常(多次尝试请求无回应)
    * interface
        * serial_interface: 串行接口类的通用接口
        * ...... 如有其它接口可放在这
    * serials
        * KDA_mock_serial.py: 继承`MockSerial`基类,是针对[KDA项目](git@gitlab.com:KD-Group/KDA.git)所需的模拟串行接口的实现
        * KDA_real_serial.py: 继承`RealSerial`基类,是针对[KDA项目](git@gitlab.com:KD-Group/KDA.git)所需的真实串行接口的实现
        * ...... 如有其它项目所需的具体实现类,可放在该目录下
* tests: 单元测试
* requirements.txt : 该项目依赖的包,在`cmd`下输入`pip install -r requirement.txt` 快速安装依赖

## 参考资料
[pyserial 官方文档](https://pyserial.readthedocs.io/en/latest/pyserial_api.html)
