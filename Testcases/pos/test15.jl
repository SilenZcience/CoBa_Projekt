# multiple returns
function test()::Float64
    a::Integer = 5
    if a % 2 == 0
        return 5.5
    else return 6.0
    end
    return 5.5
    return 6.0
end

function main()
    while false
    end
end

main()


