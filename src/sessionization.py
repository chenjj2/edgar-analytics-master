'''
This is the only script to run the code.
It runs the main function when being called by run.sh.


It consists 4 functions.
-- process_header
-- initialization
-- time_search_ip
-- main

Details of each function as below.
-- process_header
This function reads the header line and finds which column contains ip/date/time.

-- initialization
This function returns all the data structures to store information initialized with data from the first request line.

-- time_search_ip
This function returns the time (in seconds) that a certain ip has been active.

-- main
This function 
* opens the input and output file
* does initialization
* follows the flow in README
* writes remaining ip to output after finishing reading input
* closes the input and output file

'''
import sys
from datetime import datetime


def process_header(header):
	'''
	Finds the index of ip, date, time in the header
	'''

	cols = header.split(',')
	for i,col_name in enumerate(cols):
		if col_name == 'ip':
			ip_index = i
		elif col_name == 'date':
			date_index = i
		elif col_name == 'time':
			time_index = i
		else:
			pass
	return ip_index, date_index, time_index



def initialization(line_one, inactive_period, ip_index, date_index, time_index):
	'''
	Store previous time step in t_last.
	Create ip_table and store active ip as { ip: [first_request_time, last_request_time, number_of request] }.
	Create time_table and store active ip's active time as { active_time_t: [ip (which is active for time t)]}.
	'''

	# grab data from input line
	col_one = line_one.split(',')
	ip, date, time = col_one[ip_index], col_one[date_index], col_one[time_index]

	# initialize	
	t_last = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
	ip_table = {ip: [t_last, t_last, 1]}
	ip_order = {ip: 1}
	time_table = {t_loop: [] for t_loop in range(inactive_period+1)}
	time_table[0].append(ip)

	return t_last, ip_table, ip_order, time_table


def time_search_ip(time_table, ip):
	'''
	Search how long an ip has been active.
	'''
	for prev_active_time in time_table.keys():
		if ip in time_table[prev_active_time]:
			return prev_active_time


def main(input_file, inactive_file, output_file):
	''' main '''

	# read inactive_period
	with open(inactive_file,'r') as f:
		inactive_period = int(f.read())
	f.close()

	# process input and output
	with open(input_file,'r') as fin:
		# read header
		header = fin.readline()
		ip_index, date_index, time_index = process_header(header)

		with open(output_file,'w') as fout:

			# initialization
			line_one = fin.readline()
			t_last, ip_table, ip_order, time_table = initialization(line_one, inactive_period, ip_index, date_index, time_index)

			# read input from line 2 on and process
			for num, line in enumerate(fin, 2):
				columns = line.split(',')
				ip, date, time = columns[ip_index], columns[date_index], columns[time_index]

				# UPDATE time_table
				t_now = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
				
				# same time
				if t_now==t_last:
					pass
				# update time_table
				else:
					# dt in second
					dt = int((t_now - t_last).total_seconds())
					
					# dt < inactive_period and only some ip times up
					if dt < inactive_period+1:
						# collect time-out ip
						ip_timeout = []
						for t_timeout in range(inactive_period-dt+1, inactive_period+1):
							for ip_tmp in time_table[t_timeout]:
								ip_timeout.append(ip_tmp)
						# move time_table forward by dt
						for t_tmp in range(inactive_period, dt-1, -1):
							time_table[t_tmp] = time_table[t_tmp-dt]
						for t_tmp in range(dt):
							time_table[t_tmp] = []

					# all ip times up
					else:
						ip_timeout = ip_table.keys()
						time_table = {t_loop: [] for t_loop in range(inactive_period+1)}
						
					# sort with ip_order
					ip_timeout_table = { ip_tmp: ip_order[ip_tmp] for ip_tmp in ip_timeout}
					sorted_ip = sorted(ip_timeout_table, key=lambda key: ip_timeout_table[key])
					# write to output
					for ip_tmp in sorted_ip:
						first_request, last_request, n_request = ip_table[ip_tmp]
						first_datetime = first_request.strftime('%Y-%m-%d %H:%M:%S')
						last_datetime = last_request.strftime('%Y-%m-%d %H:%M:%S')
						total_time = int((last_request - first_request).total_seconds())
						fout.write(ip_tmp+','+first_datetime+','+last_datetime+','+str(total_time+1)+','+str(n_request)+'\n')
						ip_table.pop(ip_tmp)						

					# update t_last
					t_last = t_now				



				# UPDATE ip_table and ip_order
				if ip in ip_table.keys():
					# update ip_table
					first_request, last_request, n_request = ip_table[ip]
					ip_table[ip] = [first_request, t_now, n_request+1]
					# no need to update ip_order
					###
					# update time_table by removing previous record and adding to newly active list
					prev_active_time = time_search_ip(time_table, ip)
					time_table[prev_active_time].remove(ip)
					time_table[0].append(ip)
						
				# ip is new
				else:
					ip_table[ip] = [t_now, t_now, 1]
					ip_order[ip] = num
					time_table[0].append(ip)


			# remaining output after finishing reading input			
			ip_timeout = ip_table.keys()
			# sort with ip_order
			ip_timeout_table = { ip_tmp: ip_order[ip_tmp] for ip_tmp in ip_timeout}
			sorted_ip = sorted(ip_timeout_table, key=lambda key: ip_timeout_table[key])
			# write to output
			for ip_tmp in sorted_ip:
				first_request, last_request, n_request = ip_table[ip_tmp]
				first_datetime = first_request.strftime('%Y-%m-%d %H:%M:%S')
				last_datetime = last_request.strftime('%Y-%m-%d %H:%M:%S')
				total_time = int((last_request - first_request).total_seconds())
				fout.write(ip_tmp+','+first_datetime+','+last_datetime+','+str(total_time+1)+','+str(n_request)+'\n')
	


	# close files
	fin.close()
	fout.close()

	return None





if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2], sys.argv[3])