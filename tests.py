import processors

# test is in extra frames
assert processors.is_in_extra_frames(None, None) == False, "None should not be found."
assert processors.is_in_extra_frames(None, "1,2,3") == False, "None should not be found."
assert processors.is_in_extra_frames(None, "1-5") == False, "None should not be found."
assert processors.is_in_extra_frames(1, None) == False, "None should not be found."

test = ""
for i in range(1,999):
    test += f"{i},"
    
for i in range(1,999):
    assert processors.is_in_extra_frames(i, test) == True, "Frame should be found."

for i in range(1,999):
    assert processors.is_in_extra_frames(i, "1-999") == True, "Frame should be found."

assert processors.is_in_extra_frames(6, "1,2,3,4,5,7,8,9") == False, "Frame should not be found."
assert processors.is_in_extra_frames(6, "1,2,3,4,5,6,7,8,9") == True, "Frame should be found."
assert processors.is_in_extra_frames(6, "1,2,3-7,8,9") == True, "Frame should be found."
assert processors.is_in_extra_frames(3, "1,2,4-7,8,9") == False, "Frame should not be found."