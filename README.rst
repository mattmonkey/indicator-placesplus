************************
Indicator PlacesPlus 0.1
************************

**一个ubuntu unity桌面的指示器（indicator）应用**


实现功能
-------------
1. 显示Nautilus书签 （原indicator Pllaces）
#. 显示历史信息快速访问


使用方法
----------

* 运行指示器

    ::
    
      nohup  python indicator-placesplus.py &

    
    也可添加到 **启用应用程序...** 里

* 查询可用的mimetype

    ::

        ./placesconfig.py
    

配置方法
------------

1. 在配置文件 **placesplus** 里添加 **[资料]** 会生成相应的菜单
2. 在 **[资料]** 下配置 **mimetype**  会向 **资料** 菜单添加相应的历史信息. 注意要加 **=**
    
 ::

    [资料]
    application/pdf=

    [视频]
    video/x-matroska=
    video/x-ms-asf=
    video/x-ms-wmv=
    video/x-msvideo=
    application/x-matroska


=====  ===========  ======================
版本   日期          功能
0.1    2012-03-22   可配置的显示历史信息
=====  ===========  ======================
