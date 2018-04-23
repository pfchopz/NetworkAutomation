import telnetlib
#Connect to route views, run a command, collect that data for future parsing,
# as well as allow the user to input thier own AS number
def collect_output():
    HOST = "route-views3.routeviews.org"
    AS = input("Enter your Autonomous System Number: ")
    tn = telnetlib.Telnet(HOST)
    tn.write(b'show ip bgp regex ' + AS.encode('ascii') + b'\n')
    tn.write(b'exit\n')
    output = tn.read_all().decode('ascii')
    return output
#Parse the output to show only what we actually want to see
def parse_output(input):
    output = input.split("incomplete", 1)[1]
    output = output.split("Displayed", 1)[0]
    return output
#Display output of other functions
print(parse_output(collect_output()))