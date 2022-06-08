%% 参数设置
clear;
macro_block_size = 8;      % 块尺寸为16*16
w = 7;			  % 匹配次数为(2dm+1)*(2dm+1)
fprintf("########运动估计与运动预测########:\n");
fprintf("宏块大小: %d\n", macro_block_size);
fprintf("搜索范围w: %d\n", w);
fprintf("#################################\n");
figure("Name", "w="+num2str(w)+",macro_size="+num2str(macro_block_size));

%% 读入图像的预处理
% 读入参考帧的图像
ref_img = imread('18.png');    
% 读入当前帧的图像
cur_img = imread('20.png');     
% 转为灰度图，缩减维度
ref_img = rgb2gray(ref_img);
cur_img = rgb2gray(cur_img);
subplot(231); imshow(cur_img); title('当前帧图像');
subplot(232); imshow(ref_img); title('参考帧图像');
% 修改类型为浮点数便于精确计算
ref_img = double(ref_img);
cur_img = double(cur_img);

%%  搜索得到运动矢量
%[motion_vector, block_center,costs] = FullSearch(cur_img, ref_img, macro_block_size, w); %基于块的全搜索算法  
[motion_vector, block_center] = BinarySearch(cur_img, ref_img, macro_block_size, w); %基于块的全搜索算法  

subplot(233); imshow(uint8(cur_img)); title('运动矢量图'); hold on
% 参考帧指向当前帧
% 确定宏块的中心
y = block_center(1, : );
x = block_center(2, : );
% 确定每个宏块的运动矢量
v = -motion_vector(1, : );
u = -motion_vector(2, : ); 
% 绘制运动矢量图
quiver(x, y, u, v, 'r');
hold on

%% 进行运动补偿
%运动补偿后的图像：根据运动矢量计算预测帧，并传输残差帧
pred_img = motion_compensation(ref_img, motion_vector, macro_block_size); 
%计算当前帧和预测帧的峰值信噪比
subplot(234); imshow(uint8(pred_img));
title('预测帧图像');

%% 计算残差
err = cur_img - pred_img;
% 标注残差
img_err = Calibration(err); 
subplot(235); imshow(img_err); title('残差帧图像');
%  
% %% 重建图像
% %根据运动矢量指明的位置及残差帧重建图像
rebuilt_img = pred_img + err; 
subplot(236); imshow(uint8(rebuilt_img)); title('重建帧图像');



