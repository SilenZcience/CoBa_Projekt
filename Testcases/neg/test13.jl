# using variable before declaration
function main()
    testA("5", 5.5)
end

function testA(a::String, b::Float64)::Bool
    x::Integer = 1 + y
 y::Integer = 5
    println(a)
    return true
end

main()