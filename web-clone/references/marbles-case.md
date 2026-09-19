# 反例：AI 把架构抄反

单文件玻璃弹珠 demo（WebGL + SVG filter）。真架构：解析法求光线-球体交点，把光学结果编成位移图，交给 SVG `feDisplacementMap` 去扭曲**真 DOM**。WebGL 不采样页面像素。

一份 AI 分析把这套写成 ray-marching + SDF + 把 DOM 当纹理采样——另一套实现，照抄做不出原效果且更慢。

| 臆造 | 真相 | 坑型 |
|------|------|------|
| ray-marching + SDF | 解析求交 | 别默认折射 demo 用步进 |
| `sampler2D` 采 DOM | 位移图 + SVG 折射真 HTML | 搞反 GPU↔DOM 层级 |
| 单 displacement + 错 filter 链 | 双 displacement + 菲涅尔 mask | filter 链必须对真源码 |
| 常量/坐标系靠猜 | 以源码为准 | 连常量都不要信分析稿 |

AI 复刻施工图：骨架可参考，代码块一行都别直接抄。
