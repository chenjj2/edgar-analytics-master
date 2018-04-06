import sys
from datetime import datetime

def initialization(line_one, inactive_period):
	'''
	Store previous time step in t_last.
	Create ip_table and store active ip as { ip: [first_request_time, last_request_time, number_of request] }.
	Create time_table and store active ip's active time as { active_time_t: [ip (which is active for time t)]}.
	'''

	# grab data from input line
	ip, date, time = line_one.split(',')[0:3]

	# initialize	
	t_last = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
	ip_table = {ip: [t_last, t_last, 1]}
	ip_order = {ip: 1}
	time_table = {t_loop: [] for t_loop in range(inactive_period+1)}
	time_table[0].append(ip)

	return t_last, ip_table, ip_order, time_table


def time_search_ip(time_table, ip):
	'''
	Search how long ip has been active.
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
		# skip header
		fin.readline()
		with open(output_file,'w') as fout:

			# initialization
			line_one = fin.readline()
			t_last, ip_table, ip_order, time_table = initialization(line_one, inactive_period)

			# read input from line 2 on and process
			for num, line in enumerate(fin, 2):
				ip, date, time = line.split(',')[0:3]


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