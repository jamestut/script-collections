#!/usr/bin/env python3

import argparse

class _LLElement:
    def __init__(self, beginval, endval):
        '''
        Args:
            beginval: The lower value of this range block (inclusive)
            endval: The upper value of this range block (inclusive)
        '''
        # doubly linked list
        self.beginval = beginval
        self.endval = endval
        self.nextitem = None
        self.previtem = None

    def __eq__(self, other):
        return self.beginval == other.beginval and self.endval == other.endval

    def is_overlap(self, other):
        return max(self.beginval, other.beginval) <= min(self.endval, other.endval)

    def merge(self, other):
        if not self.is_overlap(other):
            raise ValueError("Must be overlapping to merge")

        self.beginval = min(self.beginval, other.beginval)
        self.endval = max(self.endval, other.endval)

    def __str__(self):
        return f'{IPStorage.ip_int_to_str(self.beginval)} - {IPStorage.ip_int_to_str(self.endval)}'

class _LinkedList:
    def __init__(self):
        self._begin = None
        self._end = None

    def append(self, v, after=None):
        if self._maybe_initial_insert(v):
            return
        if after == self._end:
            after = None
        tgt = self._end if after is None else after
        v.nextitem = tgt.nextitem
        tgt.nextitem = v
        v.previtem = tgt
        if v.nextitem:
            v.nextitem.previtem = v
        if after is None:
            self._end = v

    def prepend(self, v):
        if self._maybe_initial_insert(v):
            return
        assert not v.previtem
        v.nextitem = self._begin
        self._begin.previtem = v
        self._begin = v

    def delete(self, v):
        if v.previtem:
            v.previtem.nextitem = v.nextitem
        if v.nextitem:
            v.nextitem.previtem = v.previtem
        return v.nextitem

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    @property
    def empty(self):
        if self._begin is None or self._end is None:
            assert self._begin is None
            assert self._end is None
            return True
        return False

    def _maybe_initial_insert(self, v):
        if self.empty:
            self._begin = v
            self._end = v
            return True
        return False

class IPStorage:
    def __init__(self):
        self._data = _LinkedList()

    def add_ip_range(self, begin, end):
        newitem = _LLElement(begin, end)

        # first ever entry
        if self._data.empty:
            self._data.append(newitem)
            return

        if end <= self._data.begin.beginval:
            # can prepend?
            self._data.prepend(newitem)
        else:
            # otherwise, find existing block to append to
            extblock = self._data.begin
            while extblock is not None:
                if extblock == newitem:
                    # we have an exact match: save some cycle
                    return
                if (begin > extblock.endval):
                    if extblock.nextitem and begin > extblock.nextitem.endval:
                        extblock = extblock.nextitem
                        continue
                    self._data.append(newitem, extblock)
                    break
                if newitem.is_overlap(extblock):
                    extblock.merge(newitem)
                    newitem = extblock
                    break
                extblock = extblock.nextitem

        # further merge if needed
        extblock = newitem.nextitem
        while extblock is not None and extblock.beginval <= (newitem.endval + 1):
            newitem.endval = max(extblock.endval, newitem.endval)
            extblock = self._data.delete(extblock)

    def add_ip_subnet(self, ip, subnet_length):
        begin, end = IPStorage.compute_ip_range(ip, subnet_length)
        self.add_ip_range(begin, end)

    class _Iterator:
        def __init__(self, beginval):
            self._curpos = beginval

        def __next__(self):
            if self._curpos is None:
                raise StopIteration
            ret = (self._curpos.beginval, self._curpos.endval)
            self._curpos = self._curpos.nextitem
            return ret

    def __iter__(self):
        return IPStorage._Iterator(self._data.begin)

    def generate_minimal_ip_subnet(self):
        ret = []
        curr_ipblk = self._data.begin
        while curr_ipblk is not None:
            prevlower = curr_ipblk.beginval
            nexthigher = curr_ipblk.endval
            while prevlower <= nexthigher:
                # find the smallest subnet mask (cover the most hosts)
                for subnet_length in range(32, -2, -1):
                    if subnet_length < 0:
                        break
                    ip_begin, ip_end = IPStorage.compute_ip_range(prevlower, subnet_length)
                    if (ip_begin < prevlower) or (ip_end > nexthigher):
                        break
                subnet_length += 1
                ip_begin, ip_end = IPStorage.compute_ip_range(prevlower, subnet_length)
                ret.append((ip_begin, subnet_length))
                prevlower += (ip_end - ip_begin) + 1
            curr_ipblk = curr_ipblk.nextitem
        return ret

    def generate_inverted_ip_range(self):
        ret = []

        lower = 0
        upper = 0

        curr_ipblk = self._data.begin
        while curr_ipblk:
            upper = curr_ipblk.beginval - 1

            if upper >= lower:
                ret.append((lower, upper))

            lower = curr_ipblk.endval + 1

            curr_ipblk = curr_ipblk.nextitem

        upper = 0xFFFFFFFF
        if upper >= lower:
            ret.append((lower, upper))

        return ret

    @staticmethod
    def compute_ip_range(ip, subnet_length):
        '''
        Args:
            ip: IP address in integer
            subnet_length: Length of the subnet mask

        Returns:
            A tuple. First item is the beginning IP address ("network address").
            Second item is the last IP address ("broadcast address")
        '''
        ipv4_mask = 0xFFFFFFFF

        if not (0 <= ip <= ipv4_mask):
            raise ValueError("IPv4 out of range")
        if not (0 <= subnet_length <= 32):
            raise ValueError("Subnet mask out of range")

        rev_subnetmask = ((1 << (32 - subnet_length)) - 1)
        subnetmask = ipv4_mask ^ rev_subnetmask

        ip_begin = ip & subnetmask
        ip_end = ip | rev_subnetmask

        return ip_begin, ip_end

    @staticmethod
    def ip_str_to_int(ipstr):
        splt = ipstr.split('/', maxsplit=2)
        ipstr, subnet_length = splt[0], None if len(splt) < 2 else int(splt[1])
        splt = [int(i) for i in ipstr.split('.')]
        if len(splt) != 4:
            raise ValueError("Invalid number of IP component")
        if not all(0 <= i <= 0xFF for i in splt):
            raise ValueError("Invalid IP address component range")
        ipint = 0
        for i in range(4):
            ipint += splt[-(i + 1)] * (1 << (8 * i))
        if subnet_length is not None:
            if not (0 <= subnet_length <= 32):
                raise ValueError("Subnet mask out of range")
            return ipint, subnet_length
        return ipint

    @staticmethod
    def ip_int_to_str(ipint):
        return '.'.join((str(ipint >> (8 * (3 - i)) & 0xFF) for i in range(4)))

def main():
    ap = argparse.ArgumentParser(description='Compute IPv4 address range exclusion')
    ap.add_argument('iprange', help='IPv4 subnets to include. CIDR notation and comma separated.')
    args = ap.parse_args()
    ipranges = args.iprange.split(',')

    ipstor = IPStorage()
    for ip in ipranges:
        ipstor.add_ip_subnet(*(IPStorage.ip_str_to_int(ip)))

    rev_ipstor = IPStorage()
    for iprange in ipstor.generate_inverted_ip_range():
        rev_ipstor.add_ip_range(*iprange)
    
    for ip, subnet in rev_ipstor.generate_minimal_ip_subnet():
        print(f'{IPStorage.ip_int_to_str(ip)}/{subnet}')

if __name__ == "__main__":
    main()
