function [x_index,y_index,minc] = minCost(costs)
%       costs : 包含当前宏块所有运动估计误差代价的SAD矩阵
%       x_index : 运动矢量的垂直分量（行位移）
%       y_index : 运动矢量的水平分量（列位移）
    minc = min(min(costs));
    [x_index, y_index] = find(costs == minc);
    x_index = x_index(1);
    y_index = y_index(1);    
end