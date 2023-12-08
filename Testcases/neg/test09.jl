# wrong return type
function main()
    test("5", true)
end

function test(a::String, b::Integer)::Bool
    println(a)
    return b
end

main()