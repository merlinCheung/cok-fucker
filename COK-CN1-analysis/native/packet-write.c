================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 009ed860
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE_03bc5b10
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler15WriteBinaryDataEyN5boost10shared_ptrINS0_12PacketHeaderEEENS3_INS_4Util9ByteArrayEEEb
// ADDRESS : 02b43224
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler15WriteBinaryDataEyN5boost10shared_ptrINS0_12PacketHeaderEEENS3_INS_4Util9ByteArrayEEEb
               (long param_1,undefined8 *param_2,undefined8 *param_3,uint param_4)

{
  long *plVar1;
  long *plVar2;
  int *piVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined4 uVar8;
  undefined8 uVar9;
  ulong uVar10;
  undefined8 *puVar11;
  undefined8 uVar12;
  code *pcVar13;
  undefined8 local_c8;
  long *plStack_c0;
  undefined8 local_b8;
  long *plStack_b0;
  long *local_a8;
  long *local_a0;
  undefined8 local_98;
  long *local_90;
  undefined8 local_88;
  long *local_80;
  undefined1 auStack_78 [8];
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
  lVar7 = tpidr_el0;
  local_48 = *(long *)(lVar7 + 0x28);
                    /* try { // try from 02b4324c to 02c4327b has its CatchHandler @ 02b43304 */
  uVar9 = _Znwm(0x890);
  _ZN5Sfs2X4Util9ByteArrayC2Ev();
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_58,uVar9);
  uVar10 = _ZN5Sfs2X4Core12PacketHeader10CompressedEv(*param_2);
  if ((uVar10 & 1) != 0) {
    _ZN5Sfs2X4Util9ByteArray8CompressEv(*param_3);
  }
  uVar10 = _ZN5Sfs2X4Core12PacketHeader9EncryptedEv(*param_2);
  if ((uVar10 & 1) != 0) {
    puVar11 = *(undefined8 **)(param_1 + 0x80);
    local_68 = *param_3;
    pcVar13 = *(code **)*puVar11;
                    /* try { // try from 02b432a4 to 02c432d3 has its CatchHandler @ 02b43300 */
    local_60 = (long *)param_3[1];
    if (local_60 != (long *)0x0) {
      plVar1 = local_60 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar5) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    (*pcVar13)(puVar11,&local_68);
    plVar1 = local_60;
                    /* try { // try from 02b432d4 to 02c43337 has its CatchHandler @ 02b430ec */
    if (local_60 != (long *)0x0) {
      plVar2 = local_60 + 1;
      do {
        iVar6 = (int)*plVar2 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar5) {
          *(int *)plVar2 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*local_60 + 0x10))(local_60);
                    /* catch() { ... } // from try @ 02b432a4 with catch @ 02b43300 */
        piVar3 = (int *)((long)plVar1 + 0xc);
        do {
                    /* catch() { ... } // from try @ 02b4324c with catch @ 02b43304 */
          iVar6 = *piVar3;
                    /* catch() { ... } // from try @ 02b431f4 with catch @ 02b43308 */
                    /* catch() { ... } // from try @ 02b431b8 with catch @ 02b4330c */
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
          if (bVar5) {
            *piVar3 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
  }
  uVar9 = local_58;
  uVar8 = _ZN5Sfs2X4Core12PacketHeader6EncodeEv(*param_2);
                    /* try { // try from 02b43338 to 02c43367 has its CatchHandler @ 02b433c8 */
  _ZN5Sfs2X4Util9ByteArray9WriteByteEh(uVar9,uVar8);
  uVar10 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(*param_2);
  uVar9 = local_58;
  if ((uVar10 & 1) == 0) {
    uVar12 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    _ZN5Sfs2X4Util9ByteArray11WriteUShortEt(uVar9,uVar12);
  }
  else {
    uVar12 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    _ZN5Sfs2X4Util9ByteArray8WriteIntEi(uVar9,uVar12);
  }
  uVar9 = local_58;
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_78,*param_3);
                    /* try { // try from 02b43390 to 02c433bf has its CatchHandler @ 02b433c4 */
  _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar9,auStack_78);
  if (local_70 != (long *)0x0) {
    plVar1 = local_70 + 1;
    do {
      iVar6 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b433c0 to 02c4340f has its CatchHandler @ 02b430ec */
                    /* catch() { ... } // from try @ 02b43390 with catch @ 02b433c4 */
      (**(code **)(*local_70 + 0x10))(local_70);
                    /* catch() { ... } // from try @ 02b43338 with catch @ 02b433c8 */
      piVar3 = (int *)((long)local_70 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b43128 with catch @ 02b433cc */
        iVar6 = *piVar3;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
        if (bVar5) {
          *piVar3 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b43140 with catch @ 02b433e0 */
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  uVar10 = _ZN5Sfs2X8Bitswarm14BitSwarmClient10UseBlueBoxEv(*(undefined8 *)(param_1 + 0x28));
  if ((uVar10 & 1) == 0) {
                    /* try { // try from 02b434f4 to 02c43523 has its CatchHandler @ 02b437f4 */
    _ZN5Sfs2X8Bitswarm14BitSwarmClient6SocketEv(&local_a8,*(undefined8 *)(param_1 + 0x28));
    uVar10 = (**(code **)(*local_a8 + 8))();
    if (local_a0 != (long *)0x0) {
      plVar1 = local_a0 + 1;
      do {
        iVar6 = (int)*plVar1 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar5) {
          *(int *)plVar1 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*local_a0 + 0x10))(local_a0);
        piVar3 = (int *)((long)local_a0 + 0xc);
        do {
          iVar6 = *piVar3;
                    /* try { // try from 02b4354c to 02c4357b has its CatchHandler @ 02b437f0 */
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
          if (bVar5) {
            *piVar3 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*local_a0 + 0x18))(local_a0);
        }
      }
    }
    plVar1 = local_50;
    if ((uVar10 & 1) != 0) {
      if ((param_4 & 1) == 0) {
        local_c8 = local_58;
        plStack_c0 = local_50;
        if (local_50 != (long *)0x0) {
          plVar2 = local_50 + 1;
          do {
            cVar4 = '\x01';
            bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
            if (bVar5) {
              *(int *)plVar2 = (int)*plVar2 + 1;
              cVar4 = ExclusiveMonitorsStatus();
            }
          } while (cVar4 != '\0');
        }
        _ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                  (param_1,&local_c8);
                    /* try { // try from 02b436bc to 02c436eb has its CatchHandler @ 02b437e4 */
        if (plVar1 != (long *)0x0) {
          plVar2 = plVar1 + 1;
          do {
            iVar6 = (int)*plVar2 + -1;
            cVar4 = '\x01';
            bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
            if (bVar5) {
              *(int *)plVar2 = iVar6;
              cVar4 = ExclusiveMonitorsStatus();
            }
          } while (cVar4 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*plVar1 + 0x10))(plVar1);
            piVar3 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar3;
              cVar4 = '\x01';
              bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
              if (bVar5) {
                *piVar3 = iVar6 + -1;
                cVar4 = ExclusiveMonitorsStatus();
              }
            } while (cVar4 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
      }
      else {
        local_b8 = local_58;
        plStack_b0 = local_50;
        if (local_50 != (long *)0x0) {
          plVar2 = local_50 + 1;
          do {
            cVar4 = '\x01';
            bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
            if (bVar5) {
              *(int *)plVar2 = (int)*plVar2 + 1;
              cVar4 = ExclusiveMonitorsStatus();
            }
          } while (cVar4 != '\0');
        }
        _ZN5Sfs2X4Core12SFSIOHandler8WriteUDPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                  (param_1,&local_b8);
                    /* try { // try from 02b435a8 to 02c435bf has its CatchHandler @ 02b43874 */
        if (plVar1 != (long *)0x0) {
          plVar2 = plVar1 + 1;
          do {
            iVar6 = (int)*plVar2 + -1;
            cVar4 = '\x01';
            bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
            if (bVar5) {
              *(int *)plVar2 = iVar6;
              cVar4 = ExclusiveMonitorsStatus();
            }
          } while (cVar4 != '\0');
                    /* try { // try from 02b435c0 to 02c435d7 has its CatchHandler @ 02b437f8 */
          if (iVar6 == 0) {
            (**(code **)(*plVar1 + 0x10))(plVar1);
            piVar3 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar3;
              cVar4 = '\x01';
              bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
              if (bVar5) {
                *piVar3 = iVar6 + -1;
                cVar4 = ExclusiveMonitorsStatus();
              }
            } while (cVar4 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
      }
    }
  }
  else {
    _ZN5Sfs2X8Bitswarm14BitSwarmClient10HttpClientEv(&local_88);
                    /* try { // try from 02b43410 to 02c4343f has its CatchHandler @ 02b43448 */
    local_98 = local_58;
    local_90 = local_50;
    if (local_50 != (long *)0x0) {
      plVar1 = local_50 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar5) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    _ZN5Sfs2X8Bitswarm4BBox8BBClient4SendEN5boost10shared_ptrINS_4Util9ByteArrayEEE
              (local_88,&local_98);
    plVar1 = local_90;
    if (local_90 != (long *)0x0) {
                    /* try { // try from 02b43440 to 02c4344b has its CatchHandler @ 02b430ec */
      plVar2 = local_90 + 1;
      do {
                    /* catch() { ... } // from try @ 02b43410 with catch @ 02b43448 */
        iVar6 = (int)*plVar2 + -1;
                    /* catch() { ... } // from try @ 02b437a8 with catch @ 02b4344c
                       catch() { ... } // from try @ 02b43924 with catch @ 02b4344c */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar5) {
          *(int *)plVar2 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*local_90 + 0x10))(local_90);
        piVar3 = (int *)((long)plVar1 + 0xc);
        do {
          iVar6 = *piVar3;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
          if (bVar5) {
            *piVar3 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
    if (local_80 != (long *)0x0) {
      plVar1 = local_80 + 1;
      do {
                    /* try { // try from 02b434a4 to 02c434a7 has its CatchHandler @ 02b43868 */
        iVar6 = (int)*plVar1 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar5) {
          *(int *)plVar1 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
                    /* try { // try from 02b434bc to 02c434c7 has its CatchHandler @ 02b4385c */
        (**(code **)(*local_80 + 0x10))(local_80);
        piVar3 = (int *)((long)local_80 + 0xc);
        do {
          iVar6 = *piVar3;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
          if (bVar5) {
            *piVar3 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*local_80 + 0x18))(local_80);
        }
      }
    }
  }
                    /* try { // try from 02b4360c to 02c4363b has its CatchHandler @ 02b437ec */
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      iVar6 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar3 = (int *)((long)local_50 + 0xc);
      do {
        iVar6 = *piVar3;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
        if (bVar5) {
          *piVar3 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*local_50 + 0x18))(local_50);
      }
    }
  }
                    /* try { // try from 02b43664 to 02c43693 has its CatchHandler @ 02b437e8 */
  if (*(long *)(lVar7 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b43714 to 02c43743 has its CatchHandler @ 02b437e0 */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec13OnPacketWriteEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 02b485d8
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec13OnPacketWriteEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined *puVar6;
  undefined8 *puVar7;
  ulong uVar8;
  undefined8 *puVar9;
  undefined8 uVar10;
  long *plVar11;
  code *pcVar12;
  int iVar13;
  long *plVar14;
  undefined8 local_e0;
  long *local_d8;
  undefined8 *local_d0;
  long *local_c8;
  undefined8 local_c0;
  long *plStack_b8;
  undefined8 local_b0;
  long *plStack_a8;
  undefined8 *local_a0;
  long *local_98;
  long *local_90;
  long *local_88;
  undefined8 local_80;
  long *local_78;
  undefined1 auStack_70 [8];
  undefined8 *local_68;
  long *local_60;
  long *local_58 [2];
  long local_48;
  
  lVar5 = tpidr_el0;
  local_48 = *(long *)(lVar5 + 0x28);
  uVar8 = _ZN5Sfs2X8Bitswarm14BitSwarmClient5DebugEv(*(undefined8 *)(param_1 + 0x28));
  if ((uVar8 & 1) != 0) {
    puVar9 = (undefined8 *)_Znwm(0x18);
                    /* try { // try from 02b48618 to 02c48647 has its CatchHandler @ 02b486ac */
    puVar9[1] = 0;
    puVar9[2] = 0;
    *puVar9 = 0;
    local_60 = (long *)0x0;
    local_68 = puVar9;
    _ZN5boost6detail12shared_countC2ISt6vectorISsSaISsEEEEPT_(local_58,puVar9);
    plVar11 = local_60;
    local_60 = local_58[0];
    local_58[0] = plVar11;
    if (plVar11 != (long *)0x0) {
      plVar14 = plVar11 + 1;
      do {
        iVar13 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar13 = *piVar1;
                    /* try { // try from 02b48670 to 02c4869f has its CatchHandler @ 02b486b0 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_68,puVar9,puVar9);
    puVar7 = local_68;
                    /* catch() { ... } // from try @ 02b485c4 with catch @ 02b486a4 */
                    /* catch() { ... } // from try @ 02b4856c with catch @ 02b486a8 */
                    /* catch() { ... } // from try @ 02b48618 with catch @ 02b486ac */
                    /* catch() { ... } // from try @ 02b48670 with catch @ 02b486b0 */
                    /* catch() { ... } // from try @ 02b47364 with catch @ 02b486b4 */
    FUN_0307a6fc(local_58,"Writing message",auStack_70);
    puVar6 = PTR_DAT_03c37adf_1_03bd0478;
    puVar9 = (undefined8 *)puVar7[1];
    if (puVar9 == (undefined8 *)puVar7[2]) {
      _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJSsEEEvDpOT_(puVar7,local_58);
    }
    else {
      *puVar9 = local_58[0];
      local_58[0] = (long *)(puVar6 + 0x18);
      puVar7[1] = puVar9 + 1;
                    /* try { // try from 02b486e0 to 02c4870f has its CatchHandler @ 02b487dc */
    }
    if (local_58[0] + -3 != (long *)PTR_DAT_03c37adf_1_03bd0478) {
      plVar11 = local_58[0] + -1;
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar13 = (int)*plVar11;
        *(int *)plVar11 = iVar13 + -1;
      }
      else {
        do {
                    /* try { // try from 02b48bc8 to 02c48bd7 has its CatchHandler @ 02b48dfc */
          iVar13 = (int)*plVar11;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
          if (bVar4) {
            *(int *)plVar11 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
      }
      if (iVar13 < 1) {
        _ZdlPv(local_58[0] + -3);
      }
    }
    puVar9 = local_68;
    (**(code **)(*(long *)*param_2 + 0x10))(&local_90);
    (**(code **)(*local_90 + 0x58))(&local_80);
                    /* try { // try from 02b48738 to 02c48767 has its CatchHandler @ 02b487d8 */
    if (puVar9[1] == puVar9[2]) {
      _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(puVar9,local_80);
      plVar11 = local_78;
    }
    else {
      FUN_0307e06c();
      puVar9[1] = puVar9[1] + 8;
      plVar11 = local_78;
    }
    if (plVar11 != (long *)0x0) {
      plVar14 = plVar11 + 1;
      do {
        iVar13 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
                    /* try { // try from 02b48790 to 02c487bf has its CatchHandler @ 02b487e0 */
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    if (local_88 != (long *)0x0) {
      plVar11 = local_88 + 1;
      do {
        iVar13 = (int)*plVar11 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar4) {
          *(int *)plVar11 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b48738 with catch @ 02b487d8 */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b486e0 with catch @ 02b487dc */
      if (iVar13 == 0) {
                    /* catch() { ... } // from try @ 02b48790 with catch @ 02b487e0 */
                    /* catch() { ... } // from try @ 02b45ac8 with catch @ 02b487e4
                       catch() { ... } // from try @ 02b46540 with catch @ 02b487e4
                       catch() { ... } // from try @ 02b472fc with catch @ 02b487e4 */
                    /* catch() { ... } // from try @ 02b45960 with catch @ 02b487e8 */
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar1 = (int *)((long)local_88 + 0xc);
        do {
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
                    /* try { // try from 02b48814 to 02c48843 has its CatchHandler @ 02b4884c */
          (**(code **)(*local_88 + 0x18))(local_88);
        }
      }
    }
    uVar10 = *(undefined8 *)(param_1 + 0x18);
    local_a0 = local_68;
    local_98 = local_60;
    if (local_60 != (long *)0x0) {
      plVar11 = local_60 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar4) {
          *(int *)plVar11 = (int)*plVar11 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X7Logging6Logger4WarnEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar10,&local_a0);
    plVar11 = local_98;
                    /* try { // try from 02b48844 to 02c4884f has its CatchHandler @ 02b45924 */
    if (local_98 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b48814 with catch @ 02b4884c */
      plVar14 = local_98 + 1;
      do {
        iVar13 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
        (**(code **)(*local_98 + 0x10))(local_98);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
                    /* try { // try from 02b48898 to 02c488c7 has its CatchHandler @ 02b48900 */
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    plVar11 = local_60;
    if (local_60 != (long *)0x0) {
      plVar14 = local_60 + 1;
      do {
        iVar13 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
        (**(code **)(*local_60 + 0x10))(local_60);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
                    /* try { // try from 02b488e8 to 02c488eb has its CatchHandler @ 02b48904 */
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
  }
                    /* catch() { ... } // from try @ 02b48898 with catch @ 02b48900 */
  uVar8 = (**(code **)(*(long *)*param_2 + 0x40))();
                    /* catch() { ... } // from try @ 02b488e8 with catch @ 02b48904 */
  if ((uVar8 & 1) == 0) {
    local_c0 = *param_2;
    plVar11 = (long *)param_2[1];
    if (plVar11 != (long *)0x0) {
      plVar14 = plVar11 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = (int)*plVar14 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plStack_b8 = plVar11;
    _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
              (&local_68,uVar8,&local_c0);
    plVar14 = local_60;
    puVar9 = local_68;
    local_68 = (undefined8 *)0x0;
    local_60 = (long *)0x0;
    if (plVar11 != (long *)0x0) {
      plVar2 = plVar11 + 1;
      do {
                    /* try { // try from 02b489d8 to 02c48a1b has its CatchHandler @ 02b48e70 */
        iVar13 = (int)*plVar2 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar4) {
          *(int *)plVar2 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
  }
  else {
                    /* try { // try from 02b48908 to 02c4896f has its CatchHandler @ 02b48908
                       catch() { ... } // from try @ 02b48908 with catch @ 02b48908
                       catch() { ... } // from try @ 02b48b6c with catch @ 02b48908
                       catch() { ... } // from try @ 02b48b9c with catch @ 02b48908
                       catch() { ... } // from try @ 02b48c64 with catch @ 02b48908
                       catch() { ... } // from try @ 02b48fd0 with catch @ 02b48908 */
    local_b0 = *param_2;
    plVar11 = (long *)param_2[1];
    if (plVar11 != (long *)0x0) {
      plVar14 = plVar11 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = (int)*plVar14 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plStack_a8 = plVar11;
    _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
              (&local_68,param_1,&local_b0);
    plVar14 = local_60;
    puVar9 = local_68;
    local_68 = (undefined8 *)0x0;
    local_60 = (long *)0x0;
    if (plVar11 != (long *)0x0) {
      plVar2 = plVar11 + 1;
      do {
        iVar13 = (int)*plVar2 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar4) {
          *(int *)plVar2 = iVar13;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 == 0) {
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
                    /* try { // try from 02b48970 to 02c4897b has its CatchHandler @ 02b48e5c */
          iVar13 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar13 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b4897c to 02c4898f has its CatchHandler @ 02b48de4 */
        } while (cVar3 != '\0');
        if (iVar13 + -1 == 0) {
                    /* try { // try from 02b48990 to 02c4899b has its CatchHandler @ 02b48de0 */
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
  }
  plVar11 = (long *)*param_2;
  pcVar12 = *(code **)(*plVar11 + 0x18);
  if (plVar14 != (long *)0x0) {
    plVar2 = plVar14 + 1;
    do {
                    /* try { // try from 02b48a40 to 02c48a6f has its CatchHandler @ 02b48c70 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_d0 = puVar9;
  local_c8 = plVar14;
  (*pcVar12)(plVar11,&local_d0);
  plVar11 = local_c8;
  if (local_c8 != (long *)0x0) {
    plVar2 = local_c8 + 1;
    do {
      iVar13 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar13;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar13 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar13 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar13 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b48a94 to 02c48ac3 has its CatchHandler @ 02b48c6c */
      if (iVar13 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = *(long **)(param_1 + 8);
  local_e0 = *param_2;
  pcVar12 = *(code **)(*plVar11 + 8);
  local_d8 = (long *)param_2[1];
                    /* try { // try from 02b48ac4 to 02c48acf has its CatchHandler @ 02b48dd0 */
  if (local_d8 != (long *)0x0) {
    plVar2 = local_d8 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar12)(plVar11,&local_e0);
  plVar11 = local_d8;
  if (local_d8 != (long *)0x0) {
    plVar2 = local_d8 + 1;
    do {
                    /* try { // try from 02b48af0 to 02c48afb has its CatchHandler @ 02b48d54 */
      iVar13 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar13;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar13 == 0) {
                    /* try { // try from 02b48b08 to 02c48b13 has its CatchHandler @ 02b48cdc */
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar13 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar13 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
                    /* try { // try from 02b48b3c to 02c48b6b has its CatchHandler @ 02b48e6c */
  if (plVar14 != (long *)0x0) {
    plVar11 = plVar14 + 1;
    do {
      iVar13 = (int)*plVar11 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar13;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar13 == 0) {
      (**(code **)(*plVar14 + 0x10))(plVar14);
      piVar1 = (int *)((long)plVar14 + 0xc);
      do {
                    /* try { // try from 02b48b6c to 02c48b87 has its CatchHandler @ 02b48908 */
        iVar13 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar13 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar13 + -1 == 0) {
                    /* try { // try from 02b48b88 to 02c48b9b has its CatchHandler @ 02b48c78 */
        (**(code **)(*plVar14 + 0x18))(plVar14);
      }
    }
  }
                    /* try { // try from 02b48b9c to 02c48bc7 has its CatchHandler @ 02b48908 */
  if (*(long *)(lVar5 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b48bfc to 02c48c2b has its CatchHandler @ 02b48c74 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 02b4a104
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (undefined8 *param_1,undefined8 param_2,undefined8 *param_3)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  undefined1 uVar7;
  undefined2 uVar8;
  undefined8 uVar9;
  long *plVar10;
  code *pcVar11;
  undefined1 auStack_d8 [8];
  long *local_d0;
  undefined8 local_c8;
  long *local_c0;
  undefined2 *local_b8;
  long *local_b0;
  undefined8 local_a8;
  long *local_a0;
  undefined2 *local_98;
  long *local_90;
  undefined1 *local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  undefined1 *local_68;
  long *local_60;
  long local_58;
  
                    /* catch() { ... } // from try @ 02b49260 with catch @ 02b4a108 */
                    /* catch() { ... } // from try @ 02b4924c with catch @ 02b4a10c */
  lVar6 = tpidr_el0;
                    /* catch() { ... } // from try @ 02b49240 with catch @ 02b4a124 */
  local_58 = *(long *)(lVar6 + 0x28);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b49404 with catch @ 02b4a134
                        */
                    /* catch() { ... } // from try @ 02b49048 with catch @ 02b4a138
                       catch() { ... } // from try @ 02b49468 with catch @ 02b4a138 */
  uVar9 = _Znwm(0x38);
                    /* catch() { ... } // from try @ 02b492b0 with catch @ 02b4a13c
                       catch() { ... } // from try @ 02b496b4 with catch @ 02b4a13c */
  _ZN5Sfs2X8Entities4Data9SFSObjectC2Ev();
  *param_1 = uVar9;
  param_1[1] = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Entities4Data10ISFSObjectENS4_9SFSObjectEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (param_1,uVar9,param_1 + 1);
                    /* try { // try from 02b4a164 to 02c4a193 has its CatchHandler @ 02b4a2a0 */
  local_68 = (undefined1 *)_Znwm(1);
  *local_68 = 0;
  local_60 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIhhEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_68,local_68,&local_60);
  uVar7 = (**(code **)(*(long *)*param_3 + 0x20))();
  *local_68 = uVar7;
  plVar10 = (long *)*param_1;
  pcVar11 = *(code **)(*plVar10 + 0x1e8);
  local_78 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278;
  local_70 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278 + 8);
                    /* try { // try from 02b4a1b8 to 02c4a1e7 has its CatchHandler @ 02b4a29c */
  if (local_70 != (long *)0x0) {
    plVar1 = local_70 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_88 = local_68;
  local_80 = local_60;
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar11)(plVar10,&local_78,&local_88);
  plVar10 = local_80;
  if (local_80 != (long *)0x0) {
                    /* try { // try from 02b4a210 to 02c4a23f has its CatchHandler @ 02b4a2a4 */
    plVar1 = local_80 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_70;
  if (local_70 != (long *)0x0) {
                    /* try { // try from 02b4a268 to 02c4a297 has its CatchHandler @ 02b4a2a8 */
    plVar1 = local_70 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a1b8 with catch @ 02b4a29c
                        */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a164 with catch @ 02b4a2a0
                        */
      } while (cVar3 != '\0');
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a210 with catch @ 02b4a2a4
                        */
      if (iVar5 + -1 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a268 with catch @ 02b4a2a8
                        */
                    /* catch() { ... } // from try @ 02b49218 with catch @ 02b4a2ac */
                    /* catch() { ... } // from try @ 02b49030 with catch @ 02b4a2b0 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  local_98 = (undefined2 *)_Znwm(2);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b491ac with catch @ 02b4a2c0
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b49154 with catch @ 02b4a2c4
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b490c0 with catch @ 02b4a2c8
                        */
  *local_98 = 0;
                    /* catch() { ... } // from try @ 02b49124 with catch @ 02b4a2cc */
  local_90 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIssEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_98,local_98,&local_90);
  uVar8 = (*(code *)**(undefined8 **)*param_3)();
  *local_98 = uVar8;
                    /* try { // try from 02b4a2fc to 02c4a32b has its CatchHandler @ 02b4a388 */
  plVar10 = (long *)*param_1;
  pcVar11 = *(code **)(*plVar10 + 0x208);
  local_a8 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec9ACTION_IDE_03bcfef0;
  local_a0 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec9ACTION_IDE_03bcfef0 + 8);
  if (local_a0 != (long *)0x0) {
    plVar1 = local_a0 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_b8 = local_98;
  local_b0 = local_90;
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b4a354 to 02c4a383 has its CatchHandler @ 02b4a38c */
  (*pcVar11)(plVar10,&local_a8,&local_b8);
  plVar10 = local_b0;
  if (local_b0 != (long *)0x0) {
    plVar1 = local_b0 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a2fc with catch @ 02b4a388
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a354 with catch @ 02b4a38c
                        */
      (**(code **)(*local_b0 + 0x10))(local_b0);
                    /* catch() { ... } // from try @ 02b49088 with catch @ 02b4a390 */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_a0;
  if (local_a0 != (long *)0x0) {
                    /* try { // try from 02b4a3c0 to 02c4a3ef has its CatchHandler @ 02b4a4d8 */
    plVar1 = local_a0 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_a0 + 0x10))(local_a0);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
                    /* try { // try from 02b4a3f0 to 02c4a413 has its CatchHandler @ 02b48fe8 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)*param_1;
                    /* try { // try from 02b4a414 to 02c4a41b has its CatchHandler @ 02b4a5c8 */
                    /* try { // try from 02b4a41c to 02c4a477 has its CatchHandler @ 02b48fe8 */
  pcVar11 = *(code **)(*plVar10 + 0x378);
  local_c8 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8;
  local_c0 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8 + 8);
  if (local_c0 != (long *)0x0) {
    plVar1 = local_c0 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (**(code **)(*(long *)*param_3 + 0x10))(auStack_d8);
  (*pcVar11)(plVar10,&local_c8,auStack_d8);
  if (local_d0 != (long *)0x0) {
    plVar10 = local_d0 + 1;
    do {
                    /* try { // try from 02b4a478 to 02c4a47f has its CatchHandler @ 02b4a4dc */
      iVar5 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_d0 + 0x10))(local_d0);
      piVar2 = (int *)((long)local_d0 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02b4a4bc to 02c4a4d3 has its CatchHandler @ 02b4a4f0 */
        (**(code **)(*local_d0 + 0x18))(local_d0);
      }
    }
  }
  plVar10 = local_c0;
  if (local_c0 != (long *)0x0) {
    plVar1 = local_c0 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
                    /* try { // try from 02b4a4d4 to 02c4a517 has its CatchHandler @ 02b48fe8 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a3c0 with catch @ 02b4a4d8
                        */
    } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b4a478 with catch @ 02b4a4dc */
    if (iVar5 == 0) {
      (**(code **)(*local_c0 + 0x10))(local_c0);
                    /* catch() { ... } // from try @ 02b4a4bc with catch @ 02b4a4f0 */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
                    /* try { // try from 02b4a518 to 02c4a547 has its CatchHandler @ 02b4a5c4 */
  plVar10 = local_90;
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
                    /* try { // try from 02b4a554 to 02c4a55b has its CatchHandler @ 02b4a5c0 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b4a55c to 02c4a55f has its CatchHandler @ 02b4a5c8 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_60;
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b4a588 to 02c4a5b7 has its CatchHandler @ 02b4a5cc */
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02b4a5b8 to 02c4a5cf has its CatchHandler @ 02b48fe8 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a554 with catch @ 02b4a5c0
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a518 with catch @ 02b4a5c4
                        */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a414 with catch @ 02b4a5c8
                       catch(type#1 @ 00000000) { ... } // from try @ 02b4a55c with catch @ 02b4a5c8
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b4a588 with catch @ 02b4a5cc
                        */
                    /* try { // try from 02b4a5d0 to 02c4a607 has its CatchHandler @ 02b4a5d0
                       catch() { ... } // from try @ 02b4a5d0 with catch @ 02b4a5d0
                       catch() { ... } // from try @ 02b4a67c with catch @ 02b4a5d0
                       catch() { ... } // from try @ 02b4a704 with catch @ 02b4a5d0 */
  if (*(long *)(lVar6 + 0x28) == local_58) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// matched functions: 4 | thunk-resolved: 0
