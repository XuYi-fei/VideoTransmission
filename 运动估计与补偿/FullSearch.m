function [motion_vector,block_center,costs] = FullSearch(cur_img, ref_img, marco_blcok_size, w)
    
    %% 定义基本变量
    % search_times 记录搜索次数
    search_times = 0;
    [row, col] = size(cur_img);
    % 定义每个宏块中心点位置
    block_center = zeros(2, row*col/(marco_blcok_size^2)); 
    % 定义每个宏块运动矢量
    motion_vector = zeros(2,row*col/(marco_blcok_size^2)); 
    
    % 记录当前处理的宏块的下标
    macro_block_index = 1;
    fprintf("====================================================================\n");
    fprintf("全范围搜索:\n");
    profile on  % 开启 profile
    
    %% 全搜索核心算法
    % 当前帧起始行搜索范围，步长是块数 
    for i = 1:marco_blcok_size:row-marco_blcok_size+1     
        % 当前帧起始列搜索范围，步长是块数
        for j = 1:marco_blcok_size:col-marco_blcok_size+1
            % costs为临时变量，存储针对每个宏块的各个位置的SAD
            costs = ones(2*w+1,2*w+1)*100000;
            for m = -w: w
                for n = -w: w
                    ref_blockk_row = i+m; %参考帧搜索框起始行
                    ref_block_col = j+n; %参考帧搜索框起始列
                    % 如果超出了搜索范围，就直接退出
                    if (ref_blockk_row<1||ref_blockk_row+marco_blcok_size-1>row||ref_block_col<1||ref_block_col+marco_blcok_size-1>col)                     
                        continue;                                                            
                    end
                    search_times = search_times + 1;
                    % 计算SAD
                    costs(m+w+1,n+w+1) =...
                        SAD(cur_img(i:i+marco_blcok_size-1,j:j+marco_blcok_size-1),ref_img(ref_blockk_row:ref_blockk_row+marco_blcok_size-1,ref_block_col:ref_block_col+marco_blcok_size-1));
                end
            end
            % 更新宏块的运动向量的记录
            block_center(1,macro_block_index) = i+ marco_blcok_size/2-1;                 
            block_center(2,macro_block_index) = j+ marco_blcok_size/2-1;
         
            [min_x_index,min_y_index,~]=minCost(costs); 
            
            motion_vector(1,macro_block_index) = min_x_index-w-1; 
            motion_vector(2,macro_block_index) = min_y_index-w-1; 
            macro_block_index = macro_block_index+1;
         end
    end 
    %% 后处理，打印信息，记录profile运行结果
    % 查看profile结果
    profile viewer  
    p = profile('info');
    % 保存profile 结果
    profsave(p,'profile_results') 
    fprintf("共搜索了%d次\n", search_times);
    fprintf("====================================================================\n");
end

