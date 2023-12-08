# mismatching variable types (division is always float -> simplification)
function main()

a::Integer = 6
b::Integer = -1
b = a/2


end
main()

function test(a::String, b::Integer)


    end