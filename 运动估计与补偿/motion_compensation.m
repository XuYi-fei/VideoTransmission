function pred_img = motion_compensation(ref_img, motion_vector, macro_block_size)
    [row,col] = size(ref_img);
    macro_block_index = 1;
    for i = 1:macro_block_size:row-macro_block_size+1                
        for j = 1:macro_block_size:col-macro_block_size+1 
             pred_img(i:i+macro_block_size-1,j:j+macro_block_size-1) = ref_img(i+motion_vector(1,macro_block_index):i+motion_vector(1,macro_block_index)+macro_block_size-1, ...
                 j+motion_vector(2,macro_block_index):j+motion_vector(2,macro_block_index)+macro_block_size-1);   
             macro_block_index = macro_block_index+1;
        end
    end
end