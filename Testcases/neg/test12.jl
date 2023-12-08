# wrong argument type
function main()
    testA("5", 5)
end

function testA(a::String, b::Float64)::Bool
    println(a)
    return true
end

main()