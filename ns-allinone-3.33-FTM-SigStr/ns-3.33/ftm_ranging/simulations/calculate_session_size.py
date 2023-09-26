burst_exponent = input("Enter burst exponent value: ")
ftm_per_burst = input("Enter ftm per burst: ")
ftm_req_size = 53
ack_req_size = 38
ftm_0_0_size = 79
ack_size = 36
ftm_size = 72
paramter_set_size = 22

n_bytes = 2**int(burst_exponent)*(ftm_req_size+ack_req_size+ftm_0_0_size++ack_size+(int(ftm_per_burst)-1)*(ftm_size + ack_size)) + paramter_set_size
# n_bytes = (ftm_req_size+ack_req_size+ftm_0_0_size+ack_size+(int(ftm_per_burst)-1)*(ftm_size + ack_size))
print('----------------')
print(str(n_bytes) + " bytes per session")
print(str(2**int(burst_exponent) * (int(ftm_per_burst) - 1)) + " meassurements per entry")