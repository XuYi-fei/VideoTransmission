function cost = SAD(cur_block,ref_block)
    cost=sum(sum(abs(cur_block-ref_block))); 
end
