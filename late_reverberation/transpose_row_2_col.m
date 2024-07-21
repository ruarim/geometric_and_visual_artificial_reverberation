function [vec_in] = transpose_row_2_col(vec_in)
    % get the size of the vector
    [rows, cols] = size(vec_in);

    % check if the vector is a column vector (more rows than columns)
    if rows < cols
        % if it is a column vector, transpose it
        vec_in = vec_in';
    end
end