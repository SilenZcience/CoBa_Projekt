function main()
    a::Integer = 5
    b::Integer = 3
    begin
    if true
        a = b
        return
    else
        b = a
    end
end
while true
    println(a)
    return
end
    if a == 5
        println("yes 1")
        a = a + 1
        if false
            return
        else
            b = b
            return
        end
        # unreachable:
        println("yes 2")
    else
        a = 4
        return
        # unreachable:
        println("no 1")
    end
    # unreachable:
    a = a + 2
    a = b
end
main()

# DEBUG: Control Flow Graphs
# ====================
# main:
# -------------------------
# Nodes (#20):
#   0: set()           @ set()           interference: set()
#   1: {'a'}           @ set()           interference: set()
#   2: {'b'}           @ set()           interference: {'a'}
#   3: set()           @ set()           interference: {'b', 'a'}
#   4: {'a'}           @ {'b'}           interference: {'b'}
#   5: set()           @ set()           interference: set()
#   6: {'b'}           @ {'a'}           interference: {'a'}
#   7: set()           @ set()           interference: {'b', 'a'}
#   8: set()           @ set()           interference: {'b', 'a'}
#   9: set()           @ {'a'}           interference: {'a'}
#  10: set()           @ set()           interference: set()
#  11: set()           @ {'a'}           interference: {'b', 'a'}
#  12: set()           @ set()           interference: {'b', 'a'}
#  13: {'a'}           @ {'a'}           interference: {'b', 'a'}
#  14: set()           @ set()           interference: {'b'}
#  15: set()           @ set()           interference: set()
#  16: {'b'}           @ {'b'}           interference: {'b'}
#  17: set()           @ set()           interference: set()
#  18: {'a'}           @ set()           interference: set()
#  19: set()           @ set()           interference: set()

# Adjacency List:
#   0: {1}
#   1: {2}
#   2: {3}
#   3: {4, 6}
#   4: {5}
#   5: {}
#   6: {7}
#   7: {8}
#   8: {9, 11}
#   9: {10}
#  10: {}
#  11: {18, 12}
#  12: {13}
#  13: {14}
#  14: {16, 15}
#  15: {}
#  16: {17}
#  17: {}
#  18: {19}
#  19: {}
# -------------------------

# ====================