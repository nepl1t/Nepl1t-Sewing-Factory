#include <unistd.h>
#include <fcntl.h>

int main()
{
    char buf[0x100] = {0};
    int fd;
    
    fd = open("./flag.txt", O_RDONLY);
    read(fd, buf, 0x100);
    write(STDOUT_FILENO, buf, 0x100);
    
    return 0;
}