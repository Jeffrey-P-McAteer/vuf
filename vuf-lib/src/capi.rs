
use crate::*;

use std::convert::TryFrom;
use std::mem;

use libc::c_char;

#[no_mangle]
pub extern "C" fn vuf_get_domains_count() -> u32 {
  return get_domains().len() as u32;
}

#[no_mangle]
pub extern "C" fn vuf_get_domain(i: u32, buffer: *mut c_char, buffer_len: u32) {
  if buffer.is_null() {
    return;
  }
  // Safety: we know buffer is non-null.
  let i = usize::try_from(i).unwrap_or(std::usize::MAX); // We use u32 because of ABI compatability reasons, but rust indexes are all usize.
  let buffer_len = usize::try_from(buffer_len).unwrap_or(std::usize::MAX);
  let domains = get_domains();
  if domains.len() < i {
    let domain = &domains[i];
    for (c_idx, c_val) in domain.char_indices() {
      if c_idx + c_val.len_utf8() < buffer_len {
        // We can write c_val to the buffer, so do it.
        //let mut c_utf8_buf = [0; c_val.len_utf8()];
        if c_val.len_utf8() <= 16 { // Safety: we do not support utf-8 sequences > 16 chars wide
          let mut c_utf8_buf = [0; 16];
          c_val.encode_utf8(&mut c_utf8_buf);
          for c_utf8_buf_i in 0..c_utf8_buf.len() {
            let buffer_offset: isize = isize::try_from(c_idx+c_utf8_buf_i).unwrap_or(std::isize::MAX);
            unsafe {
              // Write utf-8 byte to buffer, transmuting the u8 representation to the C i8 (aka "char")
              *buffer.offset(buffer_offset) = std::mem::transmute::<u8, i8>( c_utf8_buf[c_utf8_buf_i] );
            }
          }
        }
      }
    }
  }
}



