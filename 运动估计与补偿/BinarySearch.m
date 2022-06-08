function [motion_vector,block_center] = BinarySearch(cur_img, ref_img, macro_block_size, dm)
    %% 定义基本变量
    % search_times 记录搜索次数
    search_times = 0;
    [row, col] = size(cur_img);
    % 定义每个宏块中心点位置
    block_center = zeros(2, row*col/(macro_block_size^2)); 
    % 定义每个宏块运动矢量
    motion_vector = zeros(2,row*col/(macro_block_size^2)); 
    % 记录当前处理的宏块的下标
    macro_block_index= 1;
    % 设置初始步长
    step = dm; 
    fprintf("====================================================================\n");
    fprintf("三步搜索法:\n");
    % 开启 profile
    profile on 
    
    %% 三步搜索法实现
    %当前帧起始行搜索范围，步长是块数 
    for i = 1:macro_block_size:row-macro_block_size+1     
        for j = 1:macro_block_size:col-macro_block_size+1 %当前帧起始列搜索范围，步长是块数
            % 每次走step这么长，一层遍历是3次，两层遍历就是9次
            
            start_row = i;
            start_col = j;
            last = 100000;
            min_row = -1;
            min_col = -1;
            % 只要step还大于0就继续循环
            while step > 0
                %costs = ones(3,3)*100000;
                for m= -step: step: step
                    for n= -step: step: step
                        ref_block_row = start_row+m; %参考帧搜索框起始行
                        ref_block_col = start_col+n; %参考帧搜索框起始列
                        search_times = search_times + 1;
                        % 如果超出搜索范围直接退出
                        if (ref_block_row < 1|| ref_block_row+macro_block_size-1 > row || ref_block_col < 1 || ref_block_col+macro_block_size-1 > col)                     
                            continue;                                                            
                        end
                        %计算SAD
                        cost = SAD(cur_img(i:i+macro_block_size-1,j:j+macro_block_size-1),ref_img(ref_block_row:ref_block_row+macro_block_size-1,ref_block_col:ref_block_col+macro_block_size-1));
                        if(last > cost)
                            last = cost;
                            min_row = ref_block_row;
                            min_col = ref_block_col;
                        end
                    end
                end
                % 每次9个点搜索结束后步长减半
      
                if step > 1
                    start_row = min_row;
                    start_col = min_col; 
                end
                step = floor(step / 2);
            end
            % 恢复初始步长
            step = dm;
            
            block_center(1,macro_block_index) = i+ macro_block_size/2-1;               
            block_center(2,macro_block_index) = j+ macro_block_size/2-1;
            
            motion_vector(1,macro_block_index) = min_row-i;
            motion_vector(2,macro_block_index) = min_col-j; 
            macro_block_index = macro_block_index+1;
         end
    end
    %% 后处理，打印信息，记录profile运行结果
    % 查看profile结果
    profile viewer  
    p = profile('info');
    % 保存profile 结果
    profsave(p,'profile_results') 
    % 打印搜索次数
    fprintf("共搜索了%d次\n", search_times);
    fprintf("====================================================================\n");
end

