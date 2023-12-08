# wrong argument types
function main()
    test("5", true)
end

function test(a::String, b::Integer)
    println(a)
end

main()