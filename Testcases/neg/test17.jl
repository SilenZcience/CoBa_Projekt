# duplicate variable names

function main()

end

function test(a::Integer, a::String)
end

function test2(a::Integer, b::String)
    a::Integer = 5
end

main()


