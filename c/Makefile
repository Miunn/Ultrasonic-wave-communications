CC = gcc
CFLAGS = -Wall -Wextra
LIB = 
SDIR = src
HDIR = include
BUILDDIR = bin
BINARY = project
CUSTOMLIBDIR = lib
MAINFILE = MAIN_C


# ==========================================================================

# listing all .cpp file inside SDIR and his child folder
SOURCES := $(foreach dir, $(wildcard $(SDIR)/*),$(wildcard $(dir)/*.c)) $(wildcard $(SDIR)/*.c)

# listing all .o file from all .cpp file from SDIR
OBJECTS := $(patsubst $(SDIR)/%.c, $(BUILDDIR)/$(BINARY)/%.o, $(SOURCES))


# ==========================================================================

all: $(BINARY) 

$(BINARY): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) -L$(CUSTOMLIBDIR) -o $@ $(LIB) -D$(MAINFILE) -lm

$(BUILDDIR)/$(BINARY)/%.o: $(SDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -I$(HDIR) -c $< -o $@ -D$(MAINFILE) -lm

full-clean: clean
	rm -rf $(foreach dir,$(wildcard $(BUILDDIR)/*), $(dir)) $(BINARY)

clean:
	rm -rf $(foreach dir,$(wildcard $(BUILDDIR)/$(BINARY)/*), $(dir)) $(BINARY)

# ==========================================================================% 
