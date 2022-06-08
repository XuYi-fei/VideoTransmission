function cal = Calibration(img)
    img = double(img);
    [row, col] = size(img);
    fmin = min(min(img));
    fm = img - fmin * ones(row, col);
    fmmax = max(max(fm));
    fs = 255 * fm ./ fmmax;
    cal = uint8(fs);
end