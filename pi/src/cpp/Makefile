prefix := /usr/local

# The recommended compiler flags for the Raspberry Pi
CCFLAGS=-Ofast -mfpu=vfp -mfloat-abi=hard -march=armv6zk -mtune=arm1176jzf-s -I/usr/include/python2.7

# define all programs
PROGRAMS = recieve_moisture
SOURCES = ${PROGRAMS:=.cpp}

all: ${PROGRAMS} 

${PROGRAMS}: ${SOURCES} 
	g++ ${CCFLAGS} -Wall -lpython2.7 -lrf24-bcm $@.cpp -o $@

clean:
	rm -rf $(PROGRAMS)

install: all
	test -d $(prefix) || mkdir $(prefix)
	test -d $(prefix)/bin || mkdir $(prefix)/bin
	for prog in $(PROGRAMS); do \
	  install -m 0755 $$prog $(prefix)/bin; \
	done

.PHONY: install
