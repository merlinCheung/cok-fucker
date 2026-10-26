================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeaderC2Ebbbb  [thunk -> 0x2bddf28]
// ADDRESS : 009e7320
================================================================

void _ZN5Sfs2X4Core12PacketHeaderC2Ebbbb
               (undefined8 *param_1,byte param_2,byte param_3,byte param_4,byte param_5)

{
                    /* catch() { ... } // from try @ 02bde050 with catch @ 02bddf28
                       catch() { ... } // from try @ 02bde130 with catch @ 02bddf28 */
  *(undefined1 *)(param_1 + 1) = 1;
  *param_1 = 0xffffffffffffffff;
  *(byte *)((long)param_1 + 9) = param_3 & 1;
  *(byte *)((long)param_1 + 10) = param_2 & 1;
  *(byte *)((long)param_1 + 0xb) = param_4 & 1;
  *(byte *)((long)param_1 + 0xc) = param_5 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 009e7760
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE_03bc2a90
  )();
  return;
}



================================================================
// FUNCTION: _ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0_
// ADDRESS : 009e7b60
================================================================

void _ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0_
               (void)

{
  (*(code *)
    PTR__ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0__03bc2c90
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 009e8ef0
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE(void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE_03bc3658
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKey3KeyEv  [thunk -> 0x2abc970]
// ADDRESS : 009e9ca0
================================================================

void _ZN5Sfs2X4Util9CryptoKey3KeyEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *(undefined8 *)(param_2 + 0x10);
  lVar4 = *(long *)(param_2 + 0x18);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 009ead60
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE_03bc4590
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 009eb290
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE_03bc4828
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv  [thunk -> 0x2b3b010]
// ADDRESS : 009eb490
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv(long param_1)

{
  int *piVar1;
  ulong uVar2;
  ulong uVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  void *__ptr;
  void *pvVar8;
  size_t __n;
  long *plVar9;
  ulong uVar10;
  long **pplVar11;
  long *plVar12;
  long lVar13;
  void *local_88;
  long *local_80;
  long *local_78;
  long *local_70;
  long local_68;
  
                    /* try { // try from 02b3b02c to 02c3b05b has its CatchHandler @ 02b3b060 */
  lVar7 = tpidr_el0;
  local_68 = *(long *)(lVar7 + 0x28);
  pvVar8 = (void *)_Znwm(0x38);
  _ZN5Sfs2X3FSM18FiniteStateMachineC2Ev();
  local_80 = (long *)0x0;
  local_88 = pvVar8;
  _ZN5boost6detail12shared_countC2IN5Sfs2X3FSM18FiniteStateMachineEEEPT_(&local_70,pvVar8);
  plVar9 = local_80;
                    /* catch() { ... } // from try @ 02b3b02c with catch @ 02b3b060 */
                    /* catch() { ... } // from try @ 02b3adb0 with catch @ 02b3b064 */
                    /* catch() { ... } // from try @ 02b3ad9c with catch @ 02b3b068 */
  local_80 = local_70;
                    /* catch() { ... } // from try @ 02b3ad90 with catch @ 02b3b06c */
  local_70 = plVar9;
                    /* catch() { ... } // from try @ 02b3ae3c with catch @ 02b3b070 */
  if (plVar9 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b3ad48 with catch @ 02b3b074 */
    plVar12 = plVar9 + 1;
    do {
      iVar6 = (int)*plVar12 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar5) {
        *(int *)plVar12 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
                    /* try { // try from 02b3b0a0 to 02c3b0cf has its CatchHandler @ 02b3b0d4 */
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_88,pvVar8,pvVar8);
  plVar9 = local_80;
  pvVar8 = local_88;
                    /* catch() { ... } // from try @ 02b3b0a0 with catch @ 02b3b0d4 */
                    /* catch() { ... } // from try @ 02b3acc8 with catch @ 02b3b0d8 */
  local_88 = (void *)0x0;
  local_80 = (long *)0x0;
  plVar12 = *(long **)(param_1 + 0x78);
  *(void **)(param_1 + 0x70) = pvVar8;
  *(long **)(param_1 + 0x78) = plVar9;
  if (plVar12 != (long *)0x0) {
    plVar9 = plVar12 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b3b108 to 02c3b13b has its CatchHandler @ 02b3b14c */
      (**(code **)(*plVar12 + 0x10))(plVar12);
      piVar1 = (int *)((long)plVar12 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar12 + 0x18))(plVar12);
      }
    }
  }
  plVar9 = local_80;
  if (local_80 != (long *)0x0) {
    plVar12 = local_80 + 1;
    do {
      iVar6 = (int)*plVar12 + -1;
                    /* catch() { ... } // from try @ 02b3b108 with catch @ 02b3b14c */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar5) {
        *(int *)plVar12 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* catch() { ... } // from try @ 02b3acb0 with catch @ 02b3b150 */
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3b180 to 02c3b1af has its CatchHandler @ 02b3b1c8 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  lVar13 = 0;
  local_88 = (void *)0x0;
  local_80 = (long *)0x0;
  local_78 = (long *)0x0;
  do {
    uVar10 = (long)local_80 - (long)local_88 >> 3;
    uVar3 = uVar10;
    if (uVar10 == 0) {
      uVar3 = 1;
    }
                    /* try { // try from 02b3b200 to 02c3b22f has its CatchHandler @ 02b3b234 */
    uVar2 = 0x1fffffffffffffff;
    if (!CARRY8(uVar3,uVar10) && uVar3 + uVar10 >> 0x3d == 0) {
      uVar2 = uVar3 + uVar10;
    }
    if (uVar2 == 0) {
                    /* catch() { ... } // from try @ 02b3b200 with catch @ 02b3b234 */
                    /* catch() { ... } // from try @ 02b3ac70 with catch @ 02b3b238 */
      pvVar8 = (void *)0x0;
    }
    else {
      if (uVar2 >> 0x3d != 0) {
                    /* WARNING: Subroutine does not return */
                    /* catch() { ... } // from try @ 02b3aa74 with catch @ 02b3b368 */
        FUN_03078b34();
      }
      pvVar8 = (void *)_Znwm(uVar2 << 3);
    }
    __ptr = local_88;
                    /* catch() { ... } // from try @ 02b3ac5c with catch @ 02b3b23c */
    __n = (long)local_80 - (long)local_88;
    *(long *)((long)pvVar8 + __n) = lVar13;
    if ((long)__n >> 3 != 0) {
                    /* catch() { ... } // from try @ 02b3ac50 with catch @ 02b3b254 */
                    /* catch() { ... } // from try @ 02b3acfc with catch @ 02b3b258 */
      memmove(pvVar8,local_88,__n);
    }
                    /* catch() { ... } // from try @ 02b3ac00 with catch @ 02b3b25c */
                    /* catch() { ... } // from try @ 02b3aba8 with catch @ 02b3b260 */
    if (__ptr != (void *)0x0) {
                    /* catch() { ... } // from try @ 02b3ab44 with catch @ 02b3b264 */
                    /* catch() { ... } // from try @ 02b3aaf0 with catch @ 02b3b268 */
      _ZdlPv(__ptr);
    }
                    /* catch() { ... } // from try @ 02b3a8e4 with catch @ 02b3b26c */
    plVar9 = (long *)((long)pvVar8 + uVar2 * 8);
                    /* catch() { ... } // from try @ 02b3a9a8 with catch @ 02b3b270 */
                    /* catch() { ... } // from try @ 02b3a810 with catch @ 02b3b274 */
                    /* catch() { ... } // from try @ 02b3ab7c with catch @ 02b3b278 */
    pplVar11 = &local_78;
    local_80 = (long *)((long)pvVar8 + __n) + 1;
    while( true ) {
      *pplVar11 = plVar9;
      local_88 = pvVar8;
      if (3 < lVar13) {
                    /* catch() { ... } // from try @ 02b3a8a0 with catch @ 02b3b288 */
        _ZN5Sfs2X3FSM18FiniteStateMachine12AddAllStatesERSt6vectorIlSaIlEE
                  (*(undefined8 *)(param_1 + 0x70),&local_88);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),0,1,0);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),1,3,1);
                    /* catch() { ... } // from try @ 02b3aa18 with catch @ 02b3b2c0 */
                    /* catch() { ... } // from try @ 02b3a964 with catch @ 02b3b2c4 */
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),1,2,2);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),2,3,3);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),3,0,4);
                    /* catch() { ... } // from try @ 02b3a7cc with catch @ 02b3b2fc */
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),3,4,5);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),4,0,6);
        _ZN5Sfs2X3FSM18FiniteStateMachine15SetCurrentStateEl(*(undefined8 *)(param_1 + 0x70),0);
        if (local_88 != (void *)0x0) {
                    /* catch() { ... } // from try @ 02b3aa08 with catch @ 02b3b334 */
          _ZdlPv(local_88);
        }
        if (*(long *)(lVar7 + 0x28) != local_68) {
                    /* WARNING: Subroutine does not return */
          __stack_chk_fail();
        }
                    /* catch() { ... } // from try @ 02b3a9fc with catch @ 02b3b34c */
                    /* catch() { ... } // from try @ 02b3a854 with catch @ 02b3b35c */
                    /* catch() { ... } // from try @ 02b3a91c with catch @ 02b3b360 */
                    /* catch() { ... } // from try @ 02b3a780 with catch @ 02b3b364 */
        return;
      }
                    /* catch() { ... } // from try @ 02b3b180 with catch @ 02b3b1c8 */
      lVar13 = lVar13 + 1;
                    /* catch() { ... } // from try @ 02b3ac7c with catch @ 02b3b1cc */
      if (local_80 == local_78) break;
      plVar9 = local_80 + 1;
      *local_80 = lVar13;
      pplVar11 = &local_80;
    }
  } while( true );
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader8BigSizedEv  [thunk -> 0x2bddfbc]
// ADDRESS : 009eba80
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 0xc);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
// ADDRESS : 009ec3d0
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb_03bc50c8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 009ec6c0
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE(void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE_03bc5240
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestD2Ev  [thunk -> 0x2a554fc]
// ADDRESS : 009ecb80
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0xb];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests16ExtensionRequestE_03bd2a90 + 0x10);
                    /* try { // try from 02a55520 to 02b55523 has its CatchHandler @ 02a55868 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
                    /* try { // try from 02a5554c to 02b55567 has its CatchHandler @ 02a55860 */
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[9];
                    /* try { // try from 02a55578 to 02b5557b has its CatchHandler @ 02a55748 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
                    /* try { // try from 02a55580 to 02b5559f has its CatchHandler @ 02a55860 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[7];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
                    /* try { // try from 02a55614 to 02b55617 has its CatchHandler @ 02a55858 */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* try { // try from 02a55630 to 02b55633 has its CatchHandler @ 02a55800 */
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 009ed760
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE_03bc5a90
  )();
  return;
}



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
// FUNCTION: _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv  [thunk -> 0x2ad0d80]
// ADDRESS : 009eda90
================================================================

void _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
                    /* try { // try from 02ad0d80 to 02bd0d83 has its CatchHandler @ 02ad0d20 */
                    /* catch() { ... } // from try @ 02ad0de4 with catch @ 02ad0d84 */
  *param_1 = *(undefined8 *)(param_2 + 0x170);
  lVar4 = *(long *)(param_2 + 0x178);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader10CompressedEv  [thunk -> 0x2bddf80]
// ADDRESS : 009edb70
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader10CompressedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 9);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 009ee9d0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE_03bc63c8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009eea10
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE_03bc63e8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 009eea60
================================================================

void _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests12LoginRequestC2ESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE_03bc6410
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl  [thunk -> 0x2bddf64]
// ADDRESS : 009eed10
================================================================

void _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl(undefined8 *param_1,undefined8 param_2)

{
  *param_1 = param_2;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestD1Ev  [thunk -> 0x2a58cf8]
// ADDRESS : 009ef1d0
================================================================

void _ZN5Sfs2X8Requests12LoginRequestD1Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0xd];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0 + 0x10);
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xb];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[9];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[7];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest6UseUDPEv  [thunk -> 0x2a55664]
// ADDRESS : 009ef260
================================================================

undefined1 _ZN5Sfs2X8Requests16ExtensionRequest6UseUDPEv(long param_1)

{
  return *(undefined1 *)(param_1 + 0x60);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader6EncodeEv  [thunk -> 0x2bde0b0]
// ADDRESS : 009ef380
================================================================

uint _ZN5Sfs2X4Core12PacketHeader6EncodeEv(long param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  if (*(char *)(param_1 + 8) != '\0') {
    uVar1 = 0xffffff80;
  }
  if (*(char *)(param_1 + 10) != '\0') {
    uVar1 = uVar1 | 0x40;
  }
  if (*(char *)(param_1 + 9) != '\0') {
    uVar1 = uVar1 | 0x20;
  }
  if (*(char *)(param_1 + 0xb) != '\0') {
    uVar1 = uVar1 | 0x10;
  }
  if (*(char *)(param_1 + 0xc) != '\0') {
    uVar1 = uVar1 | 8;
  }
                    /* try { // try from 02bde100 to 02cde12f has its CatchHandler @ 02bde13c */
  return uVar1;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009ef410
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE_03bc68e8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 009efd70
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE_03bc6d98
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 009f0420
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE_03bc70f0
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 009f0460
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE_03bc7110
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 009f0570
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE(void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE_03bc7198
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv  [thunk -> 0x2bddf5c]
// ADDRESS : 009f07b0
================================================================

undefined8 _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv(undefined8 *param_1)

{
  return *param_1;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKeyC1EN5boost10shared_ptrINS0_9ByteArrayEEES5_  [thunk -> 0x2abc814]
// ADDRESS : 009f0a50
================================================================

void _ZN5Sfs2X4Util9CryptoKeyC1EN5boost10shared_ptrINS0_9ByteArrayEEES5_
               (undefined8 *param_1,undefined8 *param_2,undefined8 *param_3)

{
  int *piVar1;
  long *plVar2;
  undefined8 uVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  long *plVar8;
  
                    /* try { // try from 02abc824 to 02bbc827 has its CatchHandler @ 02abc8ac */
  param_1[1] = 0;
  *param_1 = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  uVar3 = *param_2;
  lVar4 = param_2[1];
  if (lVar4 == 0) {
    *param_1 = uVar3;
    param_1[1] = 0;
  }
  else {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    plVar8 = (long *)param_1[1];
    *param_1 = uVar3;
    param_1[1] = lVar4;
    if (plVar8 != (long *)0x0) {
      plVar2 = plVar8 + 1;
      do {
        iVar7 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*plVar8 + 0x10))(plVar8);
        piVar1 = (int *)((long)plVar8 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
                    /* catch() { ... } // from try @ 02abc824 with catch @ 02abc8ac */
        }
      }
    }
  }
  uVar3 = *param_3;
  lVar4 = param_3[1];
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  plVar8 = (long *)param_1[3];
                    /* try { // try from 02abc8d4 to 02bbc8d7 has its CatchHandler @ 02abc7d0 */
  param_1[2] = uVar3;
  param_1[3] = lVar4;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02abc9c8 with catch @ 02abc8d8
                       catch(type#1 @ 00000000) { ... } // from try @ 02abc9f8 with catch @ 02abc8d8
                       catch(type#1 @ 00000000) { ... } // from try @ 02abca20 with catch @ 02abc8d8
                        */
  if (plVar8 != (long *)0x0) {
    plVar2 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 009f1ab0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE_03bc7c38
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandlerC2EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE  [thunk -> 0x2b3a754]
// ADDRESS : 009f1b90
================================================================

void _ZN5Sfs2X4Core12SFSIOHandlerC2EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
               (long *param_1,long *param_2)

{
  undefined *puVar1;
  int *piVar2;
  long lVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 uVar8;
  long lVar9;
  long *plVar10;
  long *plVar11;
  long local_70;
  long *local_68;
  long local_60;
  long *local_58;
  long *plStack_50;
  long local_48;
  
  lVar7 = tpidr_el0;
  local_48 = *(long *)(lVar7 + 0x28);
                    /* try { // try from 02b3a780 to 02c3a78f has its CatchHandler @ 02b3b364 */
  puVar1 = PTR__ZTVN5Sfs2X4Core12SFSIOHandlerE_03bd1598 + 0x10;
  param_1[1] = 0;
  param_1[2] = 0;
  *param_1 = (long)puVar1;
  memset(param_1 + 3,0,0x78);
                    /* try { // try from 02b3a7a8 to 02c3a7cb has its CatchHandler @ 02b3b5b4 */
  uVar8 = _Znwm(0x890);
  _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar8);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_60,uVar8);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
                    /* try { // try from 02b3a7cc to 02c3a7d7 has its CatchHandler @ 02b3b2fc */
  plVar10 = (long *)param_1[4];
  param_1[3] = lVar9;
  param_1[4] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3a810 to 02c3a83f has its CatchHandler @ 02b3b274 */
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b3a854 to 02c3a863 has its CatchHandler @ 02b3b35c */
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3a87c to 02c3a89f has its CatchHandler @ 02b3b4f0 */
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  lVar9 = *param_2;
  lVar3 = param_2[1];
  if (lVar3 != 0) {
    piVar2 = (int *)(lVar3 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
      if (bVar5) {
        *piVar2 = *piVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  plVar11 = (long *)param_1[6];
                    /* try { // try from 02b3a8a0 to 02c3a8ab has its CatchHandler @ 02b3b288 */
  param_1[5] = lVar9;
  param_1[6] = lVar3;
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b3a8e4 to 02c3a913 has its CatchHandler @ 02b3b26c */
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  _ZN5Sfs2X8Bitswarm14BitSwarmClient3LogEv(&local_60,*param_2);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
  plVar10 = (long *)param_1[8];
  param_1[7] = lVar9;
  param_1[8] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
                    /* try { // try from 02b3a91c to 02c3a92b has its CatchHandler @ 02b3b360 */
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
                    /* try { // try from 02b3a940 to 02c3a963 has its CatchHandler @ 02b3b678 */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3a964 to 02c3a96f has its CatchHandler @ 02b3b2c4 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3a9a8 to 02c3a9d7 has its CatchHandler @ 02b3b270 */
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  lVar9 = _Znwm(0x18);
  local_70 = *param_2;
  local_68 = (long *)param_2[1];
                    /* try { // try from 02b3a9dc to 02c3a9fb has its CatchHandler @ 02b3b4dc */
  if (local_68 != (long *)0x0) {
    plVar11 = local_68 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b3a9fc to 02c3aa07 has its CatchHandler @ 02b3b34c */
  _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
            (lVar9,&local_70);
  local_58 = (long *)0x0;
  local_60 = lVar9;
                    /* try { // try from 02b3aa08 to 02c3aa17 has its CatchHandler @ 02b3b334 */
  _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_(&plStack_50,lVar9);
  plVar11 = local_58;
  local_58 = plStack_50;
  plStack_50 = plVar11;
                    /* try { // try from 02b3aa18 to 02c3aa23 has its CatchHandler @ 02b3b2c0 */
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
                    /* try { // try from 02b3aa74 to 02c3aab7 has its CatchHandler @ 02b3b368 */
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_60,lVar9,lVar9);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
  plVar10 = (long *)param_1[0x11];
  param_1[0x10] = lVar9;
  param_1[0x11] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
                    /* try { // try from 02b3aaf0 to 02c3ab1f has its CatchHandler @ 02b3b268 */
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_68;
  if (local_68 != (long *)0x0) {
    plVar10 = local_68 + 1;
    do {
                    /* try { // try from 02b3ab44 to 02c3ab73 has its CatchHandler @ 02b3b264 */
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_68 + 0x10))(local_68);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b3ab7c to 02c3ab7f has its CatchHandler @ 02b3b278 */
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = (long *)param_1[10];
  param_1[9] = 0;
  param_1[10] = 0;
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
                    /* try { // try from 02b3aba8 to 02c3abd7 has its CatchHandler @ 02b3b260 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv(param_1);
                    /* try { // try from 02b3ac00 to 02c3ac2f has its CatchHandler @ 02b3b25c */
  if (*(long *)(lVar7 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE
// ADDRESS : 009f2710
================================================================

void _ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE_03bc8268
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodecD2Ev  [thunk -> 0x2b46114]
// ADDRESS : 009f3280
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodecD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[6];
  *param_1 = (long)(PTR__ZTVN5Sfs2X4Core16SFSProtocolCodecE_03bd8b58 + 0x10);
  if (plVar6 != (long *)0x0) {
                    /* try { // try from 02b4613c to 02c4616b has its CatchHandler @ 02b479bc */
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[4];
                    /* try { // try from 02b46190 to 02c4619b has its CatchHandler @ 02b481cc */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b461d0 to 02c461ff has its CatchHandler @ 02b47a48 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[2];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b46228 to 02c46257 has its CatchHandler @ 02b47a00 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 009f4070
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE_03bc8f18
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler10InitializeEv  [thunk -> 0x2b3b868]
// ADDRESS : 009f4d00
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler10InitializeEv(long param_1)

{
  int *piVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  int iVar8;
  long *plVar9;
  undefined8 local_70;
  long *local_68;
  undefined8 local_60;
  long *local_58;
  undefined8 local_50;
  long *local_48;
  undefined *local_40;
  long local_38;
  
  lVar5 = tpidr_el0;
  local_38 = *(long *)(lVar5 + 0x28);
  uVar6 = _Znwm(0x38);
                    /* try { // try from 02b3b894 to 02c3b8af has its CatchHandler @ 02b3bccc */
  plVar7 = *(long **)(param_1 + 0x10);
  if (plVar7 == (long *)0x0) {
LAB_02b3babc:
                    /* try { // try from 02b3bac4 to 02c3bad3 has its CatchHandler @ 02b3bb5c */
    local_40 = PTR__ZTVN5boost12bad_weak_ptrE_03bcea60 + 0x10;
    _ZN5boost15throw_exceptionINS_12bad_weak_ptrEEEvRKT_(&local_40);
  }
  else {
    plVar9 = plVar7 + 1;
    iVar8 = (int)plVar7[1];
    do {
      while( true ) {
        if (iVar8 == 0) goto LAB_02b3babc;
        iVar2 = (int)*plVar9;
                    /* try { // try from 02b3b8bc to 02c3b8cf has its CatchHandler @ 02b3bb34 */
        if (iVar2 == iVar8) break;
        ClearExclusiveLocal();
                    /* try { // try from 02b3b8b0 to 02c3b8bb has its CatchHandler @ 02b3bb4c */
        iVar8 = iVar2;
      }
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar8 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3b8d0 to 02c3b8db has its CatchHandler @ 02b3bb30 */
      iVar8 = iVar2;
    } while (cVar3 != '\0');
    local_60 = *(undefined8 *)(param_1 + 8);
    local_70 = *(undefined8 *)(param_1 + 0x28);
    local_68 = *(long **)(param_1 + 0x30);
    if (local_68 != (long *)0x0) {
      plVar9 = local_68 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = (int)*plVar9 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    local_58 = plVar7;
    _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
              (uVar6,&local_60,&local_70);
    local_48 = (long *)0x0;
                    /* try { // try from 02b3b920 to 02c3b94f has its CatchHandler @ 02b3bb5c */
    local_50 = uVar6;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_50,uVar6,&local_48);
    plVar7 = local_48;
    uVar6 = local_50;
    local_50 = 0;
    local_48 = (long *)0x0;
    plVar9 = *(long **)(param_1 + 0x60);
    *(undefined8 *)(param_1 + 0x58) = uVar6;
    *(long **)(param_1 + 0x60) = plVar7;
    if (plVar9 != (long *)0x0) {
      plVar7 = plVar9 + 1;
      do {
        iVar8 = (int)*plVar7 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar7,0x10);
        if (bVar4) {
          *(int *)plVar7 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar8 = *piVar1;
                    /* try { // try from 02b3b974 to 02c3b9a3 has its CatchHandler @ 02b3bb1c */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    plVar7 = local_48;
    if (local_48 != (long *)0x0) {
      plVar9 = local_48 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_48 + 0x10))(local_48);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
                    /* try { // try from 02b3b9c8 to 02c3b9f7 has its CatchHandler @ 02b3bb18 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_68;
    if (local_68 != (long *)0x0) {
      plVar9 = local_68 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3ba00 to 02c3ba03 has its CatchHandler @ 02b3bb20 */
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_68 + 0x10))(local_68);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3ba2c to 02c3ba5b has its CatchHandler @ 02b3bb14 */
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_58;
    if (local_58 != (long *)0x0) {
      plVar9 = local_58 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_58 + 0x10))(local_58);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3ba84 to 02c3bab3 has its CatchHandler @ 02b3bb10 */
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    if (*(long *)(lVar5 + 0x28) == local_38) {
      return;
    }
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b3bad4 to 02c3bb83 has its CatchHandler @ 02b3b820 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
// ADDRESS : 009f59b0
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll(void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll_03bc9bb8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_
// ADDRESS : 009f6420
================================================================

void _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_(void)

{
  (*(code *)PTR__ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT__03bca0f0
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
// ADDRESS : 009f6d90
================================================================

void _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE_03bca5a8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEN5boost10shared_ptrINS_4Util9CryptoKeyEEE
// ADDRESS : 009f6dc0
================================================================

void _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEN5boost10shared_ptrINS_4Util9CryptoKeyEEE(void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEN5boost10shared_ptrINS_4Util9CryptoKeyEEE_03bca5c0
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader9EncryptedEv  [thunk -> 0x2bddf6c]
// ADDRESS : 009f7750
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader9EncryptedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 10);
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12SFSIOHandlerES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009f7d60
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12SFSIOHandlerES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12SFSIOHandlerES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE_03bcad90
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8SmartFox20SendHandshakeRequestEb  [thunk -> 0x2a71f40]
// ADDRESS : 009f7ee0
================================================================

void _ZN5Sfs2X8SmartFox20SendHandshakeRequestEb(long param_1,ulong param_2)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  undefined *puVar7;
  undefined8 uVar8;
  int *piVar9;
  undefined8 local_a0;
  long *plStack_98;
  long local_90;
  undefined1 auStack_88 [8];
  long local_80;
  undefined8 local_78;
  long *local_70;
  long local_68;
  undefined8 local_60;
  long *local_58 [2];
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
  uVar8 = _Znwm(0x30);
  _ZN5Sfs2X8SmartFox7VersionEv(&local_78,param_1);
  FUN_0307e06c(&local_68,local_78);
  if ((param_2 & 1) == 0) {
    FUN_0307a6fc(&local_80,&DAT_0323d65d,auStack_88);
  }
  else {
    FUN_0307e06c(&local_80,*(undefined8 *)(param_1 + 0x78));
  }
  FUN_0307e06c(&local_90,*(undefined8 *)(param_1 + 0x40));
  _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs(uVar8,&local_68,&local_80,&local_90);
  local_58[0] = (long *)0x0;
  local_60 = uVar8;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_60,uVar8,local_58);
  puVar7 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_90 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar9 = (int *)(local_90 + -8);
    do {
      iVar5 = *piVar9;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 < 1) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a72130 with catch @ 02a721a4
                       catch(type#1 @ 00000000) { ... } // from try @ 02a721b4 with catch @ 02a721a4
                        */
      _ZdlPv((undefined *)(local_90 + -0x18));
    }
  }
  if ((undefined *)(local_80 + -0x18) != puVar7) {
                    /* try { // try from 02a721b0 to 02b721b3 has its CatchHandler @ 02a721b8 */
    piVar9 = (int *)(local_80 + -8);
    do {
                    /* try { // try from 02a721b4 to 02b721b7 has its CatchHandler @ 02a721a4 */
      iVar5 = *piVar9;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a721b0 with catch @ 02a721b8
                        */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
                    /* try { // try from 02a721c4 to 02b721c7 has its CatchHandler @ 02a72060 */
    if (iVar5 < 1) {
      _ZdlPv((undefined *)(local_80 + -0x18));
    }
  }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a71ed4 with catch @ 02a72020
                        */
                    /* try { // try from 02a72028 to 02b7202b has its CatchHandler @ 02a7202c */
                    /* catch() { ... } // from try @ 02a72028 with catch @ 02a7202c */
  if ((undefined *)(local_68 + -0x18) != puVar7) {
    piVar9 = (int *)(local_68 + -8);
    do {
      iVar5 = *piVar9;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 < 1) {
      _ZdlPv((undefined *)(local_68 + -0x18));
    }
  }
  if (local_70 != (long *)0x0) {
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
                    /* try { // try from 02a7204c to 02b7204f has its CatchHandler @ 02a72050 */
    if (iVar5 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a7204c with catch @ 02a72050
                        */
                    /* try { // try from 02a7205c to 02b7205f has its CatchHandler @ 02a71e70 */
      (**(code **)(*local_70 + 0x10))(local_70);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a720fc with catch @ 02a72060
                       catch(type#1 @ 00000000) { ... } // from try @ 02a7217c with catch @ 02a72060
                       catch(type#1 @ 00000000) { ... } // from try @ 02a721c4 with catch @ 02a72060
                        */
      piVar9 = (int *)((long)local_70 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  plVar1 = local_58[0];
  local_a0 = local_60;
  plStack_98 = local_58[0];
  if (local_58[0] != (long *)0x0) {
    plVar2 = local_58[0] + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  _ZN5Sfs2X8SmartFox4SendEN5boost10shared_ptrINS_8Requests8IRequestEEE(param_1,&local_a0);
  if (plVar1 != (long *)0x0) {
    plVar2 = plVar1 + 1;
    do {
      iVar5 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar1 + 0x10))(plVar1);
      piVar9 = (int *)((long)plVar1 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02a720fc to 02b720ff has its CatchHandler @ 02a72060 */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  plVar1 = local_58[0];
  if (local_58[0] != (long *)0x0) {
    plVar2 = local_58[0] + 1;
    do {
      iVar5 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02a72130 to 02b72157 has its CatchHandler @ 02a721a4 */
      (**(code **)(*local_58[0] + 0x10))(local_58[0]);
      piVar9 = (int *)((long)plVar1 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a7217c to 02b7217f has its CatchHandler @ 02a72060 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKey2IVEv  [thunk -> 0x2abc944]
// ADDRESS : 009f8010
================================================================

void _ZN5Sfs2X4Util9CryptoKey2IVEv(undefined8 *param_1,undefined8 *param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *param_2;
  lVar4 = param_2[1];
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009f8520
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE_03bcb170
  )();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009f88d0
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE_03bcb348
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader10FromBinaryEl  [thunk -> 0x2bddfd0]
// ADDRESS : 009f8990
================================================================

void _ZN5Sfs2X4Core12PacketHeader10FromBinaryEl(undefined8 *param_1,uint param_2)

{
  undefined8 *puVar1;
  
  puVar1 = (undefined8 *)_Znwm(0x10);
  *(undefined1 *)(puVar1 + 1) = 1;
  *param_1 = puVar1;
  *puVar1 = 0xffffffffffffffff;
  *(byte *)((long)puVar1 + 9) = (byte)(param_2 >> 5) & 1;
  *(byte *)((long)puVar1 + 10) = (byte)(param_2 >> 6) & 1;
                    /* try { // try from 02bde020 to 02cde04f has its CatchHandler @ 02bde074 */
  *(byte *)((long)puVar1 + 0xb) = (byte)(param_2 >> 4) & 1;
  *(byte *)((long)puVar1 + 0xc) = (byte)(param_2 >> 3) & 1;
  param_1[1] = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (param_1,puVar1,param_1 + 1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 009f8ee0
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE(void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE_03bcb650
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandlerD2Ev  [thunk -> 0x2b3b564]
// ADDRESS : 009f9510
================================================================

void _ZN5Sfs2X4Core12SFSIOHandlerD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0x11];
  *param_1 = (long)(PTR__ZTVN5Sfs2X4Core12SFSIOHandlerE_03bd1598 + 0x10);
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* catch() { ... } // from try @ 02b3b52c with catch @ 02b3b5b0 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
                    /* catch() { ... } // from try @ 02b3a7a8 with catch @ 02b3b5b4 */
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xf];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
                    /* try { // try from 02b3b5f0 to 02c3b61f has its CatchHandler @ 02b3b674 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xc];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b3b5f0 with catch @ 02b3b674 */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3a940 with catch @ 02b3b678 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[10];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* try { // try from 02b3b6b4 to 02c3b6e3 has its CatchHandler @ 02b3b794 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[8];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* try { // try from 02b3b70c to 02c3b73b has its CatchHandler @ 02b3b798 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* try { // try from 02b3b73c to 02c3b79b has its CatchHandler @ 02b3a5e0 */
  plVar6 = (long *)param_1[6];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3b6b4 with catch @ 02b3b794 */
  plVar6 = (long *)param_1[4];
                    /* catch() { ... } // from try @ 02b3b70c with catch @ 02b3b798 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
                    /* try { // try from 02b3b7e0 to 02c3b80f has its CatchHandler @ 02b3b81c */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[2];
  if (plVar6 != (long *)0x0) {
    piVar2 = (int *)((long)plVar6 + 0xc);
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
      (**(code **)(*plVar6 + 0x18))();
    }
  }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3b7e0 with catch @ 02b3b81c
                        */
                    /* try { // try from 02b3b820 to 02c3b893 has its CatchHandler @ 02b3b820
                       catch() { ... } // from try @ 02b3b820 with catch @ 02b3b820
                       catch() { ... } // from try @ 02b3bad4 with catch @ 02b3b820
                       catch() { ... } // from try @ 02b3bd28 with catch @ 02b3b820 */
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util9CryptoKeyES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 009f9890
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util9CryptoKeyES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (void)

{
  (*(code *)
    PTR__ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util9CryptoKeyES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE_03bcbb28
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequestD1Ev  [thunk -> 0x2bbd954]
// ADDRESS : 009f9bb0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequestD1Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  char cVar6;
  bool bVar7;
  int iVar8;
  long *plVar9;
  long *plVar10;
  
                    /* catch() { ... } // from try @ 02bbda08 with catch @ 02bbd968 */
  plVar10 = (long *)param_1[0x17];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests21GenericMessageRequestE_03bd08f0 + 0x10);
  if (plVar10 != (long *)0x0) {
    lVar5 = plVar10[1];
    lVar4 = *plVar10;
    for (lVar3 = lVar4; lVar5 != lVar3; lVar3 = lVar3 + 0x10) {
      plVar9 = *(long **)(lVar3 + 8);
      if (plVar9 != (long *)0x0) {
        plVar1 = plVar9 + 1;
        do {
          iVar8 = (int)*plVar1 + -1;
          cVar6 = '\x01';
          bVar7 = (bool)ExclusiveMonitorPass(plVar1,0x10);
          if (bVar7) {
            *(int *)plVar1 = iVar8;
            cVar6 = ExclusiveMonitorsStatus();
          }
        } while (cVar6 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*plVar9 + 0x10))(plVar9);
          piVar2 = (int *)((long)plVar9 + 0xc);
          do {
            iVar8 = *piVar2;
            cVar6 = '\x01';
            bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
            if (bVar7) {
              *piVar2 = iVar8 + -1;
              cVar6 = ExclusiveMonitorsStatus();
            }
          } while (cVar6 != '\0');
                    /* try { // try from 02bbd9d8 to 02cbda07 has its CatchHandler @ 02bbdaa8 */
          if (iVar8 + -1 == 0) {
            (**(code **)(*plVar9 + 0x18))(plVar9);
          }
        }
      }
    }
    plVar10[1] = lVar4;
    plVar10 = (long *)param_1[0x18];
    param_1[0x17] = 0;
    param_1[0x18] = 0;
    if (plVar10 != (long *)0x0) {
                    /* try { // try from 02bbda08 to 02cbdaab has its CatchHandler @ 02bbd968 */
      plVar9 = plVar10 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar7) {
          *(int *)plVar9 = iVar8;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar10 + 0x10))(plVar10);
        piVar2 = (int *)((long)plVar10 + 0xc);
        do {
          iVar8 = *piVar2;
          cVar6 = '\x01';
          bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar7) {
            *piVar2 = iVar8 + -1;
            cVar6 = ExclusiveMonitorsStatus();
          }
        } while (cVar6 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
  }
  plVar10 = (long *)param_1[0x18];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbd9d8 with catch @ 02bbdaa8 */
                    /* catch() { ... } // from try @ 02bbdb80 with catch @ 02bbdaac
                       catch() { ... } // from try @ 02bbdd80 with catch @ 02bbdaac */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x16];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x14];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
                    /* try { // try from 02bbdb18 to 02cbdb2b has its CatchHandler @ 02bbdbac */
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02bbdb50 to 02cbdb7f has its CatchHandler @ 02bbdba8 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x12];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdb80 to 02cbdbe3 has its CatchHandler @ 02bbdaac */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbdb50 with catch @ 02bbdba8 */
                    /* catch() { ... } // from try @ 02bbdb18 with catch @ 02bbdbac */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x10];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdbe4 to 02cbdc0f has its CatchHandler @ 02bbdd94 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0xe];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdc3c to 02cbdc6b has its CatchHandler @ 02bbdd90 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0xc];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
                    /* try { // try from 02bbdc98 to 02cbdcc7 has its CatchHandler @ 02bbdd8c */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[10];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
                    /* try { // try from 02bbdcf4 to 02cbdd23 has its CatchHandler @ 02bbdd88 */
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[8];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
                    /* try { // try from 02bbdd50 to 02cbdd7f has its CatchHandler @ 02bbdd98 */
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
                    /* try { // try from 02bbdd80 to 02cbdd9b has its CatchHandler @ 02bbdaac */
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 009fa780
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE_03bcc2a0
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler8WriteUDPEN5boost10shared_ptrINS_4Util9ByteArrayEEE  [thunk -> 0x2b43a60]
// ADDRESS : 009fad30
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler8WriteUDPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  long *plVar2;
  int *piVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  code *pcVar8;
  undefined8 local_48;
  long *local_40;
  long *local_38;
  long *local_30;
  long local_28;
  
                    /* try { // try from 02b43a6c to 02c43a9b has its CatchHandler @ 02b43c9c */
  lVar7 = tpidr_el0;
  local_28 = *(long *)(lVar7 + 0x28);
  _ZN5Sfs2X8Bitswarm14BitSwarmClient10UdpManagerEv(&local_38,*(undefined8 *)(param_1 + 0x28));
  local_48 = *param_2;
  pcVar8 = *(code **)(*local_38 + 0x18);
  local_40 = (long *)param_2[1];
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b43ac0 to 02c43aef has its CatchHandler @ 02b43c98 */
  (*pcVar8)(local_38,&local_48);
  plVar1 = local_40;
  if (local_40 != (long *)0x0) {
    plVar2 = local_40 + 1;
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
                    /* try { // try from 02b43af0 to 02c43afb has its CatchHandler @ 02b43dfc */
      (**(code **)(*local_40 + 0x10))(local_40);
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
                    /* try { // try from 02b43b1c to 02c43b27 has its CatchHandler @ 02b43d80 */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (local_30 != (long *)0x0) {
    plVar1 = local_30 + 1;
    do {
      iVar6 = (int)*plVar1 + -1;
                    /* try { // try from 02b43b34 to 02c43b3f has its CatchHandler @ 02b43d08 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_30 + 0x10))(local_30);
      piVar3 = (int *)((long)local_30 + 0xc);
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
                    /* try { // try from 02b43b68 to 02c43b97 has its CatchHandler @ 02b43e98 */
        (**(code **)(*local_30 + 0x18))(local_30);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_28) {
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b43b98 to 02c43bb3 has its CatchHandler @ 02b43934 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
// ADDRESS : 009faf00
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE_03bcc660
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 009fafd0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE_03bcc6c8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 009fb540
================================================================

void _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE_03bcc980
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs  [thunk -> 0x2bc42bc]
// ADDRESS : 009fbd70
================================================================

void _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs
               (long *param_1,undefined8 param_2,long *param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined8 uVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  code *pcVar9;
  undefined1 auStack_f0 [8];
  long *local_e8;
  undefined8 local_e0;
  long *local_d8;
  undefined1 *local_d0;
  long *local_c8;
  undefined1 auStack_c0 [8];
  long local_b8;
  undefined1 *local_b0;
  long *local_a8;
  undefined1 auStack_a0 [8];
  long *local_98;
  undefined8 local_90;
  long *local_88;
  undefined1 auStack_80 [8];
  long *local_78;
  undefined8 local_70;
  long *local_68;
  long local_58;
  
  lVar4 = tpidr_el0;
  local_58 = *(long *)(lVar4 + 0x28);
                    /* catch() { ... } // from try @ 02bc4098 with catch @ 02bc42f4 */
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,0);
  plVar8 = (long *)param_1[1];
                    /* try { // try from 02bc4304 to 02cc431b has its CatchHandler @ 02bc431c */
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests16HandshakeRequestE_03bd2400 + 0x10);
                    /* catch() { ... } // from try @ 02bc4304 with catch @ 02bc431c */
  pcVar9 = *(code **)(*plVar8 + 0x2a8);
                    /* try { // try from 02bc4320 to 02cc4323 has its CatchHandler @ 02bc4328 */
  local_70 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16HandshakeRequest7KEY_APIE_03bd8a38;
  local_68 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest7KEY_APIE_03bd8a38 + 8);
                    /* try { // try from 02bc4324 to 02cc446f has its CatchHandler @ 02bc3bf8 */
                    /* catch() { ... } // from try @ 02bc4320 with catch @ 02bc4328 */
  if (local_68 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bc3cf8 with catch @ 02bc432c */
    plVar1 = local_68 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  uVar5 = _Znwm(8);
  FUN_0307e06c(uVar5,param_2);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_80,uVar5);
  (*pcVar9)(plVar8,&local_70,auStack_80);
  if (local_78 != (long *)0x0) {
    plVar8 = local_78 + 1;
    do {
      iVar7 = (int)*plVar8 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
                    /* catch() { ... } // from try @ 02bc3f0c with catch @ 02bc4394 */
                    /* catch() { ... } // from try @ 02bc3e70 with catch @ 02bc4398 */
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar6 = (int *)((long)local_78 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_78 + 0x18))(local_78);
      }
    }
  }
  plVar8 = local_68;
  if (local_68 != (long *)0x0) {
    plVar1 = local_68 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_68 + 0x10))(local_68);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  plVar8 = (long *)param_1[1];
  pcVar9 = *(code **)(*plVar8 + 0x2a8);
  local_90 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16HandshakeRequest15KEY_CLIENT_TYPEE_03bda620;
  local_88 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest15KEY_CLIENT_TYPEE_03bda620 + 8);
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  uVar5 = _Znwm(8);
  FUN_0307e06c(uVar5,param_4);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_a0,uVar5);
  (*pcVar9)(plVar8,&local_90,auStack_a0);
  if (local_98 != (long *)0x0) {
    plVar8 = local_98 + 1;
    do {
      iVar7 = (int)*plVar8 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar6 = (int *)((long)local_98 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_98 + 0x18))(local_98);
      }
    }
  }
  plVar8 = local_88;
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  local_b0 = (undefined1 *)_Znwm(1);
  *local_b0 = 0;
  local_a8 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIbbEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_b0,local_b0,&local_a8);
  *local_b0 = 1;
  plVar8 = (long *)param_1[1];
  pcVar9 = *(code **)(*plVar8 + 0x1c0);
  FUN_0307a6fc(&local_b8,&DAT_03245e63,auStack_c0);
  local_d0 = local_b0;
  local_c8 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar1 = local_a8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar9)(plVar8,&local_b8,&local_d0);
  plVar8 = local_c8;
  if (local_c8 != (long *)0x0) {
    plVar1 = local_c8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if ((undefined *)(local_b8 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_b8 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_b8 + -0x18));
    }
  }
  if (*(long *)(*param_3 + -0x18) != 0) {
    plVar8 = (long *)param_1[1];
    pcVar9 = *(code **)(*plVar8 + 0x2a8);
    local_e0 = *(undefined8 *)
                PTR__ZN5Sfs2X8Requests16HandshakeRequest22KEY_RECONNECTION_TOKENE_03bd7580;
    local_d8 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest22KEY_RECONNECTION_TOKENE_03bd7580
                         + 8);
    if (local_d8 != (long *)0x0) {
      plVar1 = local_d8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    uVar5 = _Znwm(8);
    FUN_0307e06c(uVar5,param_3);
                    /* try { // try from 02bc4698 to 02cc47ab has its CatchHandler @ 02bc4698
                       catch() { ... } // from try @ 02bc4698 with catch @ 02bc4698
                       catch() { ... } // from try @ 02bc47b4 with catch @ 02bc4698 */
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_f0,uVar5);
    (*pcVar9)(plVar8,&local_e0,auStack_f0);
    if (local_e8 != (long *)0x0) {
      plVar8 = local_e8 + 1;
      do {
        iVar7 = (int)*plVar8 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
        if (bVar3) {
          *(int *)plVar8 = iVar7;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_e8 + 0x10))(local_e8);
        piVar6 = (int *)((long)local_e8 + 0xc);
        do {
          iVar7 = *piVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar3) {
            *piVar6 = iVar7 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*local_e8 + 0x18))(local_e8);
        }
      }
    }
    plVar8 = local_d8;
    if (local_d8 != (long *)0x0) {
      plVar1 = local_d8 + 1;
      do {
        iVar7 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar7;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_d8 + 0x10))(local_d8);
        piVar6 = (int *)((long)plVar8 + 0xc);
        do {
          iVar7 = *piVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar3) {
            *piVar6 = iVar7 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
        }
      }
    }
  }
  plVar8 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar1 = local_a8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02bc47ac to 02cc47b3 has its CatchHandler @ 02bc47b4 */
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
                    /* catch() { ... } // from try @ 02bc47ac with catch @ 02bc47b4
                       try { // try from 02bc47b4 to 02cc47c7 has its CatchHandler @ 02bc4698 */
  if (*(long *)(lVar4 + 0x28) != local_58) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE  [thunk -> 0x2b43c68]
// ADDRESS : 009fbec0
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  code *pcVar7;
  undefined1 auStack_58 [8];
  long *local_50;
  long *local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
                    /* try { // try from 02b43c80 to 02c43c8f has its CatchHandler @ 02b43e9c */
  local_38 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02b43c90 to 02c43ccf has its CatchHandler @ 02b43934 */
  _ZN5Sfs2X8Bitswarm14BitSwarmClient6SocketEv(&local_48,*(undefined8 *)(param_1 + 0x28));
                    /* catch() { ... } // from try @ 02b43ac0 with catch @ 02b43c98 */
                    /* catch() { ... } // from try @ 02b43a6c with catch @ 02b43c9c */
                    /* catch() { ... } // from try @ 02b43c28 with catch @ 02b43ca0 */
                    /* catch() { ... } // from try @ 02b43bb4 with catch @ 02b43ca4 */
  pcVar7 = *(code **)(*local_48 + 0x40);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_58,*param_2);
  (*pcVar7)(local_48,auStack_58);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
                    /* try { // try from 02b43cd0 to 02c43cff has its CatchHandler @ 02b43d04 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)local_50 + 0xc);
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
                    /* catch() { ... } // from try @ 02b43cd0 with catch @ 02b43d04 */
                    /* catch() { ... } // from try @ 02b43b34 with catch @ 02b43d08 */
        (**(code **)(*local_50 + 0x18))(local_50);
      }
    }
  }
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
                    /* try { // try from 02b43d38 to 02c43d6b has its CatchHandler @ 02b43d7c */
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)local_40 + 0xc);
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
        (**(code **)(*local_40 + 0x18))(local_40);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
                    /* catch() { ... } // from try @ 02b43d38 with catch @ 02b43d7c */
                    /* catch() { ... } // from try @ 02b43b1c with catch @ 02b43d80 */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util22DelegateThreeArgumentsIN5boost10shared_ptrINS_4Core12PacketHeaderEEENS3_INS0_9ByteArrayEEEbE6InvokeES6_S8_b
// ADDRESS : 009fc3f0
================================================================

void _ZN5Sfs2X4Util22DelegateThreeArgumentsIN5boost10shared_ptrINS_4Core12PacketHeaderEEENS3_INS0_9ByteArrayEEEbE6InvokeES6_S8_b
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X4Util22DelegateThreeArgumentsIN5boost10shared_ptrINS_4Core12PacketHeaderEEENS3_INS0_9ByteArrayEEEbE6InvokeES6_S8_b_03bcd0d8
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 009fd800
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE_03bcdae0
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 009fdea0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (void)

{
  (*(code *)
    PTR__ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE_03bcde30
  )();
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Bitswarm13PendingPacketC1EN5boost10shared_ptrINS_4Core12PacketHeaderEEE  [thunk -> 0x2bdda90]
// ADDRESS : 009fe450
================================================================

void _ZN5Sfs2X8Bitswarm13PendingPacketC1EN5boost10shared_ptrINS_4Core12PacketHeaderEEE
               (undefined8 *param_1,undefined8 *param_2)

{
  int *piVar1;
  long lVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  uint uVar7;
  undefined8 uVar8;
  long *plVar9;
  long *plVar10;
  undefined8 local_50;
  long *local_48;
  undefined8 local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  param_1[1] = 0;
  *param_1 = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  uVar8 = *param_2;
  lVar2 = param_2[1];
  if (lVar2 == 0) {
    *param_1 = uVar8;
    param_1[1] = 0;
  }
  else {
    piVar1 = (int *)(lVar2 + 8);
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar4) {
        *piVar1 = *piVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02bddad8 to 02cddadf has its CatchHandler @ 02bddb44 */
    } while (cVar3 != '\0');
    plVar9 = (long *)param_1[1];
    *param_1 = uVar8;
    param_1[1] = lVar2;
    if (plVar9 != (long *)0x0) {
      plVar10 = plVar9 + 1;
      do {
        iVar5 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
                    /* try { // try from 02bddb08 to 02cddb37 has its CatchHandler @ 02bddb48 */
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar5 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
  }
                    /* catch() { ... } // from try @ 02bddad8 with catch @ 02bddb44 */
  uVar8 = _Znwm(0x890);
                    /* catch() { ... } // from try @ 02bddb08 with catch @ 02bddb48 */
                    /* catch() { ... } // from try @ 02bddbe4 with catch @ 02bddb4c
                       catch() { ... } // from try @ 02bddc28 with catch @ 02bddb4c */
  _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar8);
  local_48 = (long *)0x0;
  local_50 = uVar8;
  _ZN5boost6detail12shared_countC2IN5Sfs2X4Util9ByteArrayEEEPT_(&local_40,uVar8);
                    /* try { // try from 02bddb68 to 02cddb6f has its CatchHandler @ 02bddc04 */
  local_48 = (long *)local_40;
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_50,uVar8,uVar8);
  plVar9 = local_48;
  uVar8 = local_50;
  local_50 = 0;
  local_48 = (long *)0x0;
  plVar10 = (long *)param_1[3];
  param_1[2] = uVar8;
  param_1[3] = plVar9;
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02bddbb4 to 02cddbe3 has its CatchHandler @ 02bddc00 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar9 = local_48;
                    /* try { // try from 02bddbe4 to 02cddc1b has its CatchHandler @ 02bddb4c */
  if (local_48 != (long *)0x0) {
    plVar10 = local_48 + 1;
    do {
      iVar5 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* catch() { ... } // from try @ 02bddbb4 with catch @ 02bddc00 */
                    /* catch() { ... } // from try @ 02bddb68 with catch @ 02bddc04 */
      (**(code **)(*local_48 + 0x10))(local_48);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar1;
                    /* try { // try from 02bddc1c to 02cddc1f has its CatchHandler @ 02bddc20 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02bddc1c with catch @ 02bddc20 */
      } while (cVar3 != '\0');
                    /* try { // try from 02bddc24 to 02cddc27 has its CatchHandler @ 02bddc30 */
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02bddc28 to 02cddc33 has its CatchHandler @ 02bddb4c */
                    /* catch() { ... } // from try @ 02bddc24 with catch @ 02bddc30 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  uVar8 = param_1[2];
  uVar7 = _ZN5Sfs2X4Core12PacketHeader10CompressedEv(*param_2);
  _ZN5Sfs2X4Util9ByteArray10CompressedEb(uVar8,uVar7 & 1);
  if (*(long *)(lVar6 + 0x28) == local_38) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bddc88 with catch @ 02bddc68
                       catch(type#1 @ 00000000) { ... } // from try @ 02bddcd4 with catch @ 02bddc68
                        */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: Java_org_cocos2dx_ext_Native_BlowFishDecrypt
// ADDRESS : 0185527c
================================================================

void Java_org_cocos2dx_ext_Native_BlowFishDecrypt
               (long *param_1,undefined8 param_2,undefined8 param_3)

{
  char cVar1;
  bool bVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  long lVar6;
  int iVar7;
  int *piVar8;
  undefined8 uVar9;
  void *local_10;
  long local_8;
  
  local_8 = *(long *)PTR___stack_chk_guard_03bd37f0;
  FUN_02d607a4(1,&DAT_0312a268,"Java_org_cocos2dx_ext_Native_NativeBlowFish");
  uVar5 = (**(code **)(*param_1 + 0x5c0))(param_1,param_3,0);
  iVar3 = (**(code **)(*param_1 + 0x558))(param_1,param_3);
  if (DAT_03c1a2c8 == 0) {
    lVar6 = _Znwm(0x1058);
    FUN_00a7aa8c();
    cVar1 = *(char *)(lVar6 + 0x1054);
    DAT_03c1a2c8 = lVar6;
  }
  else {
    cVar1 = *(char *)(DAT_03c1a2c8 + 0x1054);
  }
  if (cVar1 == '\0') {
    lVar6 = FUN_01854444();
    FUN_0307e06c(&local_10,lVar6 + 0x1d8);
    if (DAT_03c1a2c8 == 0) {
      lVar6 = _Znwm(0x1058);
      FUN_00a7aa8c();
      DAT_03c1a2c8 = lVar6;
    }
    FUN_00a7aaa4(DAT_03c1a2c8,local_10,*(undefined4 *)((long)local_10 + -0x18),0);
    if ((undefined *)((long)local_10 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar7 = *(int *)((long)local_10 + -8);
        *(int *)((long)local_10 + -8) = iVar7 + -1;
      }
      else {
        piVar8 = (int *)((long)local_10 + -8);
        do {
          iVar7 = *piVar8;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
          if (bVar2) {
            *piVar8 = iVar7 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar7 < 1) {
        _ZdlPv((undefined *)((long)local_10 + -0x18));
      }
    }
    if (DAT_03c1a2c8 == 0) {
      lVar6 = _Znwm(0x1058);
      FUN_00a7aa8c();
      DAT_03c1a2c8 = lVar6;
    }
  }
  uVar9 = 0;
  FUN_00a7b7c8(DAT_03c1a2c8,uVar5,iVar3);
  local_10 = (void *)0x0;
  uVar4 = FUN_02d96ccc(uVar5,(long)iVar3,&local_10);
  if (local_10 != (void *)0x0) {
    uVar9 = (**(code **)(*param_1 + 0x580))(param_1,uVar4);
    (**(code **)(*param_1 + 0x680))(param_1,uVar9,0,uVar4,local_10);
    free(local_10);
  }
  (**(code **)(*param_1 + 0x600))(param_1,param_3,uVar5,0);
  if (local_8 == *(long *)PTR___stack_chk_guard_03bd37f0) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail(uVar9);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestC2ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
// ADDRESS : 02a5451c
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestC2ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
               (long *param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4,
               uint param_5)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  undefined8 local_78;
  long *plStack_70;
  undefined8 local_68;
  long *local_60;
  long local_58 [2];
  long local_48;
  
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,0xd);
  puVar5 = PTR__ZTVN5Sfs2X8Requests16ExtensionRequestE_03bd2a90;
  param_1[9] = 0;
  param_1[8] = 0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  *param_1 = (long)(puVar5 + 0x10);
  FUN_0307e06c(local_58,param_2);
  local_68 = *param_3;
  local_60 = (long *)param_3[1];
  if (local_60 != (long *)0x0) {
    plVar8 = local_60 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = (int)*plVar8 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_78 = *param_4;
  plVar8 = (long *)param_4[1];
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  plStack_70 = plVar8;
  _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
            (param_1,local_58,&local_68,&local_78,param_5 & 1);
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  plVar8 = local_60;
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if ((undefined *)(local_58[0] + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_58[0] + -0x18));
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
// ADDRESS : 02a54970
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
               (long param_1,undefined8 param_2,long *param_3,undefined8 *param_4,byte param_5)

{
  int *piVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 uVar8;
  long *plVar9;
  long *plVar10;
  undefined8 local_68;
  long *local_60;
  long local_58;
  
  lVar7 = tpidr_el0;
  local_58 = *(long *)(lVar7 + 0x28);
  *(undefined8 *)(param_1 + 0x18) = 1;
  uVar8 = _Znwm(8);
  FUN_0307e06c(uVar8,param_2);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar8);
  plVar10 = local_60;
  uVar8 = local_68;
  local_68 = 0;
  local_60 = (long *)0x0;
  plVar9 = *(long **)(param_1 + 0x38);
  *(undefined8 *)(param_1 + 0x30) = uVar8;
  *(long **)(param_1 + 0x38) = plVar10;
  if (plVar9 != (long *)0x0) {
    plVar10 = plVar9 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02a54a30 to 02b54a33 has its CatchHandler @ 02a54a3c */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar10 = local_60;
                    /* catch() { ... } // from try @ 02a5495c with catch @ 02a54a3c
                       catch() { ... } // from try @ 02a54a30 with catch @ 02a54a3c */
  if (local_60 != (long *)0x0) {
    plVar9 = local_60 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02a54a5c to 02b54a5f has its CatchHandler @ 02a54860 */
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  lVar2 = *param_3;
  lVar3 = param_3[1];
  if (lVar3 != 0) {
    piVar1 = (int *)(lVar3 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar5) {
        *piVar1 = *piVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  plVar10 = *(long **)(param_1 + 0x48);
  *(long *)(param_1 + 0x40) = lVar2;
  *(long *)(param_1 + 0x48) = lVar3;
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  uVar8 = *param_4;
  lVar2 = param_4[1];
  if (lVar2 != 0) {
    piVar1 = (int *)(lVar2 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar5) {
        *piVar1 = *piVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  plVar10 = *(long **)(param_1 + 0x58);
  *(undefined8 *)(param_1 + 0x50) = uVar8;
  *(long *)(param_1 + 0x58) = lVar2;
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  *(byte *)(param_1 + 0x60) = param_5 & 1;
  if (*param_3 == 0) {
    uVar8 = _Znwm(0x38);
    _ZN5Sfs2X8Entities4Data9SFSObjectC2Ev();
    local_60 = (long *)0x0;
    local_68 = uVar8;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Entities4Data10ISFSObjectENS4_9SFSObjectEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_68,uVar8,&local_60);
    plVar10 = local_60;
    uVar8 = local_68;
    local_68 = 0;
    local_60 = (long *)0x0;
    plVar9 = *(long **)(param_1 + 0x48);
    *(undefined8 *)(param_1 + 0x40) = uVar8;
    *(long **)(param_1 + 0x48) = plVar10;
    if (plVar9 != (long *)0x0) {
      plVar10 = plVar9 + 1;
      do {
        iVar6 = (int)*plVar10 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar5) {
          *(int *)plVar10 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar6 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    plVar10 = local_60;
    if (local_60 != (long *)0x0) {
      plVar9 = local_60 + 1;
      do {
        iVar6 = (int)*plVar9 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar5) {
          *(int *)plVar9 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
                    /* catch() { ... } // from try @ 02a54cb0 with catch @ 02a54c70
                       catch() { ... } // from try @ 02a54d80 with catch @ 02a54c70 */
        (**(code **)(*local_60 + 0x10))(local_60);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
          iVar6 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_58) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEE
// ADDRESS : 02a54d44
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEE
               (long *param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  undefined8 local_78;
  long *plStack_70;
  undefined8 local_68;
  long *local_60;
  long local_58 [2];
  long local_48;
  
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,0xd);
  puVar5 = PTR__ZTVN5Sfs2X8Requests16ExtensionRequestE_03bd2a90;
                    /* try { // try from 02a54d80 to 02b54e63 has its CatchHandler @ 02a54c70 */
  param_1[9] = 0;
  param_1[8] = 0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  *param_1 = (long)(puVar5 + 0x10);
  FUN_0307e06c(local_58,param_2);
  local_68 = *param_3;
  local_60 = (long *)param_3[1];
  if (local_60 != (long *)0x0) {
    plVar8 = local_60 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = (int)*plVar8 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_78 = *param_4;
  plVar8 = (long *)param_4[1];
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  plStack_70 = plVar8;
  _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
            (param_1,local_58,&local_68,&local_78,0);
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
                    /* catch() { ... } // from try @ 02a54d00 with catch @ 02a54e14 */
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  plVar8 = local_60;
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
                    /* catch() { ... } // from try @ 02a54ee0 with catch @ 02a54ea4
                       catch() { ... } // from try @ 02a54f44 with catch @ 02a54ea4 */
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if ((undefined *)(local_58[0] + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02a54f14 to 02b54f17 has its CatchHandler @ 02a54fd8 */
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_58[0] + -0x18));
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a54ee0 to 02b54f0b has its CatchHandler @ 02a54ea4 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 02a55194
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestC1ESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (long *param_1,undefined8 param_2,undefined8 *param_3)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  undefined8 local_68;
  undefined8 uStack_60;
  undefined8 local_58;
  long *plStack_50;
  long local_48 [2];
  long local_38;
  
  lVar4 = tpidr_el0;
  local_38 = *(long *)(lVar4 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,0xd);
  puVar5 = PTR__ZTVN5Sfs2X8Requests16ExtensionRequestE_03bd2a90;
  param_1[9] = 0;
  param_1[8] = 0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  *param_1 = (long)(puVar5 + 0x10);
  FUN_0307e06c(local_48,param_2);
                    /* catch() { ... } // from try @ 02a5511c with catch @ 02a551f0 */
  local_58 = *param_3;
  plVar8 = (long *)param_3[1];
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
                    /* try { // try from 02a55214 to 02b55217 has its CatchHandler @ 02a55004 */
  local_68 = 0;
  uStack_60 = 0;
                    /* catch() { ... } // from try @ 02a55248 with catch @ 02a55218
                       catch() { ... } // from try @ 02a552e4 with catch @ 02a55218
                       catch() { ... } // from try @ 02a5578c with catch @ 02a55218
                       catch() { ... } // from try @ 02a5581c with catch @ 02a55218 */
  plStack_50 = plVar8;
  _ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb
            (param_1,local_48,&local_58,&local_68,0);
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
                    /* try { // try from 02a55248 to 02b552c7 has its CatchHandler @ 02a55218 */
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if ((undefined *)(local_48[0] + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_48[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
                    /* try { // try from 02a552e4 to 02b55303 has its CatchHandler @ 02a55218 */
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
                    /* try { // try from 02a552d8 to 02b552db has its CatchHandler @ 02a55808 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_48[0] + -0x18));
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestD2Ev
// ADDRESS : 02a554fc
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0xb];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests16ExtensionRequestE_03bd2a90 + 0x10);
                    /* try { // try from 02a55520 to 02b55523 has its CatchHandler @ 02a55868 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
                    /* try { // try from 02a5554c to 02b55567 has its CatchHandler @ 02a55860 */
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[9];
                    /* try { // try from 02a55578 to 02b5557b has its CatchHandler @ 02a55748 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
                    /* try { // try from 02a55580 to 02b5559f has its CatchHandler @ 02a55860 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[7];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
                    /* try { // try from 02a55614 to 02b55617 has its CatchHandler @ 02a55858 */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* try { // try from 02a55630 to 02b55633 has its CatchHandler @ 02a55800 */
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequestD0Ev
// ADDRESS : 02a55640
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequestD0Ev(void *param_1)

{
                    /* try { // try from 02a5564c to 02b5564f has its CatchHandler @ 02a55860 */
  _ZN5Sfs2X8Requests16ExtensionRequestD2Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest6UseUDPEv
// ADDRESS : 02a55664
================================================================

undefined1 _ZN5Sfs2X8Requests16ExtensionRequest6UseUDPEv(long param_1)

{
  return *(undefined1 *)(param_1 + 0x60);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02a5566c
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE(long param_1)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  long *plVar6;
  undefined8 *puVar7;
  undefined8 uVar8;
  long lVar9;
  long **pplVar10;
  int iVar11;
  long *plVar12;
  long *local_90;
  long *local_88;
  long *local_80;
  long *local_78;
  undefined8 local_70;
  undefined8 uStack_68;
  long *local_60;
  long *plStack_58;
  undefined1 auStack_50 [8];
  long *local_48;
  long *local_40;
  long local_38;
  
  lVar4 = tpidr_el0;
  local_38 = *(long *)(lVar4 + 0x28);
  plVar6 = (long *)_Znwm(0x10);
  *plVar6 = (long)plVar6;
  plVar6[1] = (long)plVar6;
  local_40 = (long *)0x0;
  local_48 = plVar6;
  _ZN5boost6detail12shared_countC2ISt4listISsSaISsEEEEPT_(&local_60,plVar6);
  local_40 = local_60;
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_48,plVar6,plVar6);
  plVar6 = local_48;
  if ((*(long **)(param_1 + 0x30) == (long *)0x0) ||
     (*(long *)(**(long **)(param_1 + 0x30) + -0x18) == 0)) {
    FUN_0307a6fc(&local_60,"Missing extension command",auStack_50);
    puVar7 = (undefined8 *)_Znwm(0x18);
    *puVar7 = 0;
    puVar7[1] = 0;
    puVar5 = PTR_DAT_03c37adf_1_03bd0478;
    puVar7[2] = local_60;
    local_60 = (long *)(puVar5 + 0x18);
    FUN_0303d178(puVar7,plVar6);
    if (local_60 + -3 != (long *)puVar5) {
                    /* try { // try from 02a559b0 to 02b55aef has its CatchHandler @ 02a55b50 */
      plVar6 = local_60 + -1;
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar11 = (int)*plVar6;
        *(int *)plVar6 = iVar11 + -1;
      }
      else {
        do {
          iVar11 = (int)*plVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
          if (bVar3) {
            *(int *)plVar6 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      if (iVar11 < 1) {
        _ZdlPv(local_60 + -3);
        lVar9 = *(long *)(param_1 + 0x40);
        plVar6 = local_48;
        goto joined_r0x02a55a14;
      }
    }
  }
  lVar9 = *(long *)(param_1 + 0x40);
  plVar6 = local_48;
joined_r0x02a55a14:
  local_48 = plVar6;
  if (lVar9 == 0) {
                    /* catch() { ... } // from try @ 02a55578 with catch @ 02a55748 */
    FUN_0307a6fc(&local_60,"Missing extension parameters",auStack_50);
    puVar7 = (undefined8 *)_Znwm(0x18);
    *puVar7 = 0;
    puVar7[1] = 0;
    puVar5 = PTR_DAT_03c37adf_1_03bd0478;
    puVar7[2] = local_60;
    local_60 = (long *)(puVar5 + 0x18);
    FUN_0303d178(puVar7,plVar6);
    if (local_60 + -3 != (long *)puVar5) {
      plVar6 = local_60 + -1;
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar11 = (int)*plVar6;
        *(int *)plVar6 = iVar11 + -1;
      }
      else {
        do {
          iVar11 = (int)*plVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
          if (bVar3) {
            *(int *)plVar6 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      if (iVar11 < 1) {
        _ZdlPv(local_60 + -3);
      }
    }
  }
                    /* try { // try from 02a5578c to 02b5578f has its CatchHandler @ 02a55218 */
  plVar6 = local_40;
                    /* catch() { ... } // from try @ 02a55484 with catch @ 02a55790 */
  plVar12 = (long *)*local_48;
  if (local_48 != plVar12) {
    do {
      plVar12 = (long *)*plVar12;
    } while (local_48 != plVar12);
    uVar8 = _Znwm(8);
                    /* catch() { ... } // from try @ 02a55354 with catch @ 02a557c0 */
    FUN_0307a6fc(uVar8,"ExtensionCall request error",&local_70);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_60,uVar8);
    local_70 = _Znwm(0x48);
    pplVar10 = &local_60;
    local_80 = local_60;
    local_78 = plStack_58;
    if (plStack_58 != (long *)0x0) {
      plStack_58 = plStack_58 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plStack_58,0x10);
        if (bVar3) {
          *(int *)plStack_58 = (int)*plStack_58 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02a5545c with catch @ 02a55800
                       catch() { ... } // from try @ 02a5548c with catch @ 02a55800
                       catch() { ... } // from try @ 02a55630 with catch @ 02a55800 */
      } while (cVar2 != '\0');
    }
                    /* catch() { ... } // from try @ 02a552d8 with catch @ 02a55808 */
    local_90 = local_48;
    local_88 = local_40;
    if (local_40 != (long *)0x0) {
      pplVar10 = (long **)(local_40 + 1);
      do {
                    /* try { // try from 02a5581c to 02b5581f has its CatchHandler @ 02a55218 */
                    /* catch() { ... } // from try @ 02a5532c with catch @ 02a55820 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(pplVar10,0x10);
        if (bVar3) {
          *(int *)pplVar10 = *(int *)pplVar10 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
                    /* catch() { ... } // from try @ 02a553ac with catch @ 02a55828 */
    _ZN5Sfs2X10Exceptions18SFSValidationErrorC2EN5boost10shared_ptrISsEENS3_ISt4listISsSaISsEEEE
              (pplVar10,local_70,&local_80,&local_90);
    uStack_68 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions18SFSValidationErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_70,local_70,(ulong)&local_70 | 8);
    plVar6 = local_88;
    if (local_88 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02a55380 with catch @ 02a55858
                       catch() { ... } // from try @ 02a553b4 with catch @ 02a55858
                       catch() { ... } // from try @ 02a55614 with catch @ 02a55858 */
      plVar12 = local_88 + 1;
      do {
                    /* catch() { ... } // from try @ 02a5554c with catch @ 02a55860
                       catch() { ... } // from try @ 02a55580 with catch @ 02a55860
                       catch() { ... } // from try @ 02a5564c with catch @ 02a55860 */
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02a55520 with catch @ 02a55868 */
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
                    /* catch() { ... } // from try @ 02a558b4 with catch @ 02a55870
                       catch() { ... } // from try @ 02a55b4c with catch @ 02a55870 */
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar1 = (int *)((long)plVar6 + 0xc);
        do {
          iVar11 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    plVar6 = local_78;
    if (local_78 != (long *)0x0) {
      plVar12 = local_78 + 1;
      do {
                    /* try { // try from 02a558b4 to 02b55907 has its CatchHandler @ 02a55870 */
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_78 + 0x10))(local_78);
        piVar1 = (int *)((long)plVar6 + 0xc);
        do {
          iVar11 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    puVar7 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar8 = uStack_68;
    puVar7[1] = 0;
    uStack_68 = 0;
    puVar7[1] = uVar8;
    *puVar7 = local_70;
    local_70 = 0;
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar7,
                PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEEE_03bd18c8,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEED2Ev_03bd87c0);
  }
  if (local_40 != (long *)0x0) {
    plVar12 = local_40 + 1;
    do {
      iVar11 = (int)*plVar12 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar3) {
        *(int *)plVar12 = iVar11;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar11 == 0) {
                    /* try { // try from 02a5595c to 02b5595f has its CatchHandler @ 02a55b28 */
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar1 = (int *)((long)plVar6 + 0xc);
      do {
        iVar11 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar11 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 + -1 == 0) {
                    /* try { // try from 02a55984 to 02b55987 has its CatchHandler @ 02a55b90 */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  if (*(long *)(lVar4 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16ExtensionRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02a55e24
================================================================

void _ZN5Sfs2X8Requests16ExtensionRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE(long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  undefined8 uVar8;
  code *pcVar9;
  undefined8 local_a8;
  long *local_a0;
  undefined8 local_98;
  long *local_90;
  undefined8 *local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  undefined8 *local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  undefined8 local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x2a8);
  local_48 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16ExtensionRequest7KEY_CMDE_03bd27b8;
  local_40 = *(long **)(PTR__ZN5Sfs2X8Requests16ExtensionRequest7KEY_CMDE_03bd27b8 + 8);
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_58 = *(undefined8 *)(param_1 + 0x30);
  local_50 = *(long **)(param_1 + 0x38);
  if (local_50 != (long *)0x0) {
                    /* try { // try from 02a55e90 to 02b55f3f has its CatchHandler @ 02a55f5c */
    plVar1 = local_50 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar9)(plVar7,&local_48,&local_58);
  plVar7 = local_50;
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
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
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_40;
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* catch() { ... } // from try @ 02a55e90 with catch @ 02a55f5c */
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  local_68 = (undefined8 *)_Znwm(8);
  *local_68 = 0;
  local_60 = (long *)0x0;
                    /* try { // try from 02a55f80 to 02b55f83 has its CatchHandler @ 02a55d74 */
                    /* catch() { ... } // from try @ 02a55fc8 with catch @ 02a55f84
                       catch() { ... } // from try @ 02a56190 with catch @ 02a55f84 */
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_68,local_68,&local_60);
  if (*(undefined8 **)(param_1 + 0x50) == (undefined8 *)0x0) {
    uVar8 = 0xffffffffffffffff;
  }
  else {
    uVar8 = (**(code **)**(undefined8 **)(param_1 + 0x50))();
  }
  *local_68 = uVar8;
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x228);
  local_78 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16ExtensionRequest8KEY_ROOME_03bd4e30;
  local_70 = *(long **)(PTR__ZN5Sfs2X8Requests16ExtensionRequest8KEY_ROOME_03bd4e30 + 8);
                    /* try { // try from 02a55fc8 to 02b56073 has its CatchHandler @ 02a55f84 */
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
  (*pcVar9)(plVar7,&local_78,&local_88);
  plVar7 = local_80;
  if (local_80 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_70;
  if (local_70 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
      do {
                    /* try { // try from 02a560a0 to 02b5614f has its CatchHandler @ 02a5616c */
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x378);
  local_98 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16ExtensionRequest10KEY_PARAMSE_03bd1f70;
  local_90 = *(long **)(PTR__ZN5Sfs2X8Requests16ExtensionRequest10KEY_PARAMSE_03bd1f70 + 8);
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
  local_a8 = *(undefined8 *)(param_1 + 0x40);
  local_a0 = *(long **)(param_1 + 0x48);
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
  (*pcVar9)(plVar7,&local_98,&local_a8);
  plVar7 = local_a0;
  if (local_a0 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02a560a0 with catch @ 02a5616c */
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_90;
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
                    /* try { // try from 02a56190 to 02b56193 has its CatchHandler @ 02a55f84 */
                    /* catch() { ... } // from try @ 02a561d0 with catch @ 02a56194
                       catch() { ... } // from try @ 02a56360 with catch @ 02a56194 */
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* try { // try from 02a561d0 to 02b56273 has its CatchHandler @ 02a56194 */
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_60;
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
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 02a5768c
================================================================

void _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (long *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
               undefined8 *param_5)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  undefined8 local_78;
  long *plStack_70;
  long local_68;
  long local_60;
  long local_58 [2];
  long local_48;
  
                    /* catch() { ... } // from try @ 02a5761c with catch @ 02a5768c */
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
                    /* try { // try from 02a576b4 to 02b576b7 has its CatchHandler @ 02a57528 */
                    /* catch() { ... } // from try @ 02a576f4 with catch @ 02a576b8
                       catch() { ... } // from try @ 02a5788c with catch @ 02a576b8 */
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,1);
  puVar5 = PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[0xd] = 0;
  param_1[0xc] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[8] = 0;
  *param_1 = (long)(puVar5 + 0x10);
  FUN_0307e06c(local_58,param_2);
                    /* try { // try from 02a576f4 to 02b577eb has its CatchHandler @ 02a576b8 */
  FUN_0307e06c(&local_60,param_3);
  FUN_0307e06c(&local_68,param_4);
  local_78 = *param_5;
  plVar8 = (long *)param_5[1];
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  plStack_70 = plVar8;
  _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,local_58,&local_60,&local_68,&local_78);
  if (plVar8 != (long *)0x0) {
    plVar1 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  puVar5 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_68 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_68 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_68 + -0x18));
    }
  }
  if ((undefined *)(local_60 + -0x18) != puVar5) {
    piVar6 = (int *)(local_60 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
                    /* try { // try from 02a5788c to 02b5788f has its CatchHandler @ 02a576b8 */
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_60 + -0x18));
    }
  }
  if ((undefined *)(local_58[0] + -0x18) != puVar5) {
    piVar6 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_58[0] + -0x18));
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a577f4 to 02b577f7 has its CatchHandler @ 02a57864 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 02a57bdc
================================================================

void _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (long param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
               undefined8 *param_5)

{
  int *piVar1;
  long lVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  undefined8 uVar7;
  long *plVar8;
  long *plVar9;
  undefined8 local_68;
  long *local_60;
  long local_58;
  
  lVar6 = tpidr_el0;
  local_58 = *(long *)(lVar6 + 0x28);
  uVar7 = _Znwm(8);
  FUN_0307e06c(uVar7,param_2);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar7);
  plVar8 = local_60;
  uVar7 = local_68;
  local_68 = 0;
  local_60 = (long *)0x0;
  plVar9 = *(long **)(param_1 + 0x48);
  *(undefined8 *)(param_1 + 0x40) = uVar7;
  *(long **)(param_1 + 0x48) = plVar8;
  if (plVar9 != (long *)0x0) {
    plVar8 = plVar9 + 1;
    do {
      iVar5 = (int)*plVar8 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar4) {
        *(int *)plVar8 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar8 = local_60;
  if (local_60 != (long *)0x0) {
    plVar9 = local_60 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  uVar7 = _Znwm(8);
  FUN_0307e06c(uVar7,param_3);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar7);
  plVar8 = local_60;
  uVar7 = local_68;
  local_68 = 0;
  local_60 = (long *)0x0;
  plVar9 = *(long **)(param_1 + 0x58);
  *(undefined8 *)(param_1 + 0x50) = uVar7;
  *(long **)(param_1 + 0x58) = plVar8;
  if (plVar9 != (long *)0x0) {
    plVar8 = plVar9 + 1;
    do {
      iVar5 = (int)*plVar8 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar4) {
        *(int *)plVar8 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar8 = local_60;
  if (local_60 != (long *)0x0) {
    plVar9 = local_60 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  uVar7 = _Znwm(8);
  FUN_0307e06c(uVar7,param_4);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar7);
  plVar8 = local_60;
  uVar7 = local_68;
  local_68 = 0;
  local_60 = (long *)0x0;
  plVar9 = *(long **)(param_1 + 0x38);
  *(undefined8 *)(param_1 + 0x30) = uVar7;
  *(long **)(param_1 + 0x38) = plVar8;
  if (plVar9 != (long *)0x0) {
    plVar8 = plVar9 + 1;
    do {
      iVar5 = (int)*plVar8 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar4) {
        *(int *)plVar8 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar8 = local_60;
  if (local_60 != (long *)0x0) {
    plVar9 = local_60 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  uVar7 = *param_5;
  lVar2 = param_5[1];
  if (lVar2 != 0) {
    piVar1 = (int *)(lVar2 + 8);
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar4) {
        *piVar1 = *piVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  plVar8 = *(long **)(param_1 + 0x68);
  *(undefined8 *)(param_1 + 0x60) = uVar7;
  *(long *)(param_1 + 0x68) = lVar2;
  if (plVar8 != (long *)0x0) {
    plVar9 = plVar8 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_58) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSs
// ADDRESS : 02a57f94
================================================================

void _ZN5Sfs2X8Requests12LoginRequestC2ESsSsSs
               (long *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  int *piVar5;
  int iVar6;
  undefined8 local_78;
  undefined8 uStack_70;
  long local_68;
  long local_60;
  long local_58 [2];
  long local_48;
  
  lVar3 = tpidr_el0;
  local_48 = *(long *)(lVar3 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,1);
  puVar4 = PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[0xd] = 0;
  param_1[0xc] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[8] = 0;
  *param_1 = (long)(puVar4 + 0x10);
  FUN_0307e06c(local_58,param_2);
  FUN_0307e06c(&local_60,param_3);
  FUN_0307e06c(&local_68,param_4);
  local_78 = 0;
  uStack_70 = 0;
  _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,local_58,&local_60,&local_68,&local_78);
  puVar4 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_68 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
                    /* try { // try from 02a58090 to 02b580db has its CatchHandler @ 02a58060 */
    piVar5 = (int *)(local_68 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
                    /* try { // try from 02a58100 to 02b58103 has its CatchHandler @ 02a58060 */
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_68 + -0x18));
    }
  }
  if ((undefined *)(local_60 + -0x18) != puVar4) {
    piVar5 = (int *)(local_60 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_60 + -0x18));
    }
  }
                    /* catch() { ... } // from try @ 02a58070 with catch @ 02a58060
                       catch() { ... } // from try @ 02a58090 with catch @ 02a58060
                       catch() { ... } // from try @ 02a58100 with catch @ 02a58060 */
  if ((undefined *)(local_58[0] + -0x18) != puVar4) {
    piVar5 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
                    /* catch() { ... } // from try @ 02a58088 with catch @ 02a580ec */
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_58[0] + -0x18));
    }
  }
                    /* try { // try from 02a58070 to 02b58083 has its CatchHandler @ 02a58060 */
  if (*(long *)(lVar3 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a58088 to 02b5808b has its CatchHandler @ 02a580ec */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestC1ESsSs
// ADDRESS : 02a5840c
================================================================

void _ZN5Sfs2X8Requests12LoginRequestC1ESsSs(long *param_1,undefined8 param_2,undefined8 param_3)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  int *piVar5;
  int iVar6;
  undefined8 local_70;
  undefined8 uStack_68;
  undefined1 auStack_60 [8];
  long local_58;
  long local_50;
  long local_48 [2];
  long local_38;
  
  lVar3 = tpidr_el0;
  local_38 = *(long *)(lVar3 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,1);
  puVar4 = PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[0xd] = 0;
  param_1[0xc] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[8] = 0;
  *param_1 = (long)(puVar4 + 0x10);
  FUN_0307e06c(local_48,param_2);
  FUN_0307e06c(&local_50,param_3);
  FUN_0307a6fc(&local_58,&DAT_0323d65d,auStack_60);
  local_70 = 0;
  uStack_68 = 0;
  _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,local_48,&local_50,&local_58,&local_70);
  puVar4 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_58 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar5 = (int *)(local_58 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_58 + -0x18));
    }
  }
  if ((undefined *)(local_50 + -0x18) != puVar4) {
    piVar5 = (int *)(local_50 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_50 + -0x18));
    }
  }
  if ((undefined *)(local_48[0] + -0x18) != puVar4) {
    piVar5 = (int *)(local_48[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_48[0] + -0x18));
    }
  }
  if (*(long *)(lVar3 + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestC2ESs
// ADDRESS : 02a58880
================================================================

void _ZN5Sfs2X8Requests12LoginRequestC2ESs(long *param_1,undefined8 param_2)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  int *piVar5;
  int iVar6;
  undefined8 local_78;
  undefined8 uStack_70;
  undefined1 auStack_68 [8];
  long local_60;
  undefined1 auStack_58 [8];
  long local_50;
  long local_48 [2];
  long local_38;
  
  lVar3 = tpidr_el0;
  local_38 = *(long *)(lVar3 + 0x28);
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,1);
  puVar4 = PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0;
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[0xd] = 0;
  param_1[0xc] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[8] = 0;
                    /* catch() { ... } // from try @ 02a588d4 with catch @ 02a588c4
                       catch() { ... } // from try @ 02a588f4 with catch @ 02a588c4
                       catch() { ... } // from try @ 02a58964 with catch @ 02a588c4 */
  *param_1 = (long)(puVar4 + 0x10);
                    /* try { // try from 02a588d4 to 02b588e7 has its CatchHandler @ 02a588c4 */
  FUN_0307e06c(local_48,param_2);
  FUN_0307a6fc(&local_50,&DAT_0323d65d,auStack_58);
                    /* try { // try from 02a588ec to 02b588ef has its CatchHandler @ 02a58950 */
                    /* try { // try from 02a588f4 to 02b5893f has its CatchHandler @ 02a588c4 */
  FUN_0307a6fc(&local_60,&DAT_0323d65d,auStack_68);
  local_78 = 0;
  uStack_70 = 0;
  _ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,local_48,&local_50,&local_60,&local_78);
  puVar4 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_60 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar5 = (int *)(local_60 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_60 + -0x18));
    }
  }
  if ((undefined *)(local_50 + -0x18) != puVar4) {
    piVar5 = (int *)(local_50 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_50 + -0x18));
    }
  }
                    /* catch() { ... } // from try @ 02a588ec with catch @ 02a58950 */
  if ((undefined *)(local_48[0] + -0x18) != puVar4) {
    piVar5 = (int *)(local_48[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar6 = *piVar5;
      *piVar5 = iVar6 + -1;
    }
    else {
      do {
        iVar6 = *piVar5;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar5,0x10);
        if (bVar2) {
          *piVar5 = iVar6 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar6 < 1) {
      _ZdlPv((undefined *)(local_48[0] + -0x18));
    }
  }
  if (*(long *)(lVar3 + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a58964 to 02b58967 has its CatchHandler @ 02a588c4 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestD1Ev
// ADDRESS : 02a58cf8
================================================================

void _ZN5Sfs2X8Requests12LoginRequestD1Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0xd];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests12LoginRequestE_03bd0ef0 + 0x10);
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xb];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[9];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[7];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequestD0Ev
// ADDRESS : 02a58e98
================================================================

void _ZN5Sfs2X8Requests12LoginRequestD0Ev(void *param_1)

{
  _ZN5Sfs2X8Requests12LoginRequestD1Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02a58ebc
================================================================

void _ZN5Sfs2X8Requests12LoginRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  char cVar1;
  bool bVar2;
  undefined *puVar3;
  undefined *puVar4;
  long lVar5;
  undefined8 *puVar6;
  undefined8 uVar7;
  undefined **ppuVar8;
  long *plVar9;
  int *piVar10;
  int iVar11;
  long *plVar12;
  undefined8 local_100;
  long *local_f8;
  long local_f0;
  long *local_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  long local_d0;
  long *plStack_c8;
  undefined8 local_c0;
  long *plStack_b8;
  undefined8 local_b0;
  long *local_a8;
  undefined *local_a0;
  long *local_98;
  undefined *local_90;
  long *local_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined *local_68;
  long *plStack_60;
  undefined *local_58;
  long *local_50;
  long local_48;
  
  lVar5 = tpidr_el0;
  local_48 = *(long *)(lVar5 + 0x28);
  _ZN5Sfs2X8SmartFox6MySelfEv(&local_58,*param_2);
  plVar9 = local_50;
  puVar3 = local_58;
  if (local_50 != (long *)0x0) {
    plVar12 = local_50 + 1;
    do {
      iVar11 = (int)*plVar12 + -1;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar2) {
        *(int *)plVar12 = iVar11;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
    if (iVar11 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar10 = (int *)((long)plVar9 + 0xc);
      do {
        iVar11 = *piVar10;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar2) {
          *piVar10 = iVar11 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  if (puVar3 != (undefined *)0x0) {
    lVar5 = _Znwm(0x10);
    *(long *)lVar5 = lVar5;
    *(long *)(lVar5 + 8) = lVar5;
    _ZN5boost10shared_ptrISt4listISsSaISsEEEC2IS3_EEPT_(&local_58,lVar5);
    puVar4 = local_58;
    FUN_0307a6fc(&local_68,"You are already logged in. Logout first",&local_c0);
    puVar6 = (undefined8 *)_Znwm(0x18);
    *puVar6 = 0;
    puVar6[1] = 0;
    puVar3 = PTR_DAT_03c37adf_1_03bd0478;
    puVar6[2] = local_68;
    local_68 = puVar3 + 0x18;
    FUN_0303d178(puVar6,puVar4);
    if (local_68 + -0x18 != puVar3) {
      piVar10 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar11 = *piVar10;
        *piVar10 = iVar11 + -1;
      }
      else {
        do {
          iVar11 = *piVar10;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar2) {
            *piVar10 = iVar11 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar11 < 1) {
        _ZdlPv(local_68 + -0x18);
      }
    }
    uVar7 = _Znwm(8);
    FUN_0307a6fc(uVar7,"LoginRequest Error",&local_80);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar7);
    local_80 = _Znwm(0x48);
    ppuVar8 = &local_68;
    local_90 = local_68;
    local_88 = plStack_60;
    if (plStack_60 != (long *)0x0) {
      plStack_60 = plStack_60 + 1;
      do {
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(plStack_60,0x10);
        if (bVar2) {
          *(int *)plStack_60 = (int)*plStack_60 + 1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    local_a0 = local_58;
    local_98 = local_50;
    if (local_50 != (long *)0x0) {
      ppuVar8 = (undefined **)(local_50 + 1);
      do {
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(ppuVar8,0x10);
        if (bVar2) {
          *(int *)ppuVar8 = *(int *)ppuVar8 + 1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    _ZN5Sfs2X10Exceptions18SFSValidationErrorC2EN5boost10shared_ptrISsEENS3_ISt4listISsSaISsEEEE
              (ppuVar8,local_80,&local_90,&local_a0);
    uStack_78 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions18SFSValidationErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_80,local_80,(ulong)&local_80 | 8);
    plVar9 = local_98;
    if (local_98 != (long *)0x0) {
      plVar12 = local_98 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar2) {
          *(int *)plVar12 = iVar11;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_98 + 0x10))(local_98);
        piVar10 = (int *)((long)plVar9 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar2) {
            *piVar10 = iVar11 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    plVar9 = local_88;
    if (local_88 != (long *)0x0) {
      plVar12 = local_88 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar2) {
          *(int *)plVar12 = iVar11;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar10 = (int *)((long)plVar9 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar2) {
            *piVar10 = iVar11 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    puVar6 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar7 = uStack_78;
    puVar6[1] = 0;
    uStack_78 = 0;
    puVar6[1] = uVar7;
    *puVar6 = local_80;
    local_80 = 0;
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar6,
                PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEEE_03bd18c8,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEED2Ev_03bd87c0);
  }
  if ((*(long **)(param_1 + 0x30) == (long *)0x0) ||
     (*(long *)(**(long **)(param_1 + 0x30) + -0x18) == 0)) {
    _ZN5Sfs2X8SmartFox6ConfigEv(&local_58,*param_2);
    plVar9 = local_50;
    puVar3 = local_58;
    if (local_50 != (long *)0x0) {
      plVar12 = local_50 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar2) {
          *(int *)plVar12 = iVar11;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_50 + 0x10))(local_50);
        piVar10 = (int *)((long)plVar9 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar2) {
            *piVar10 = iVar11 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    if (puVar3 != (undefined *)0x0) {
      uVar7 = _Znwm(8);
      _ZN5Sfs2X8SmartFox6ConfigEv(&local_b0,*param_2);
      _ZN5Sfs2X4Util10ConfigData4ZoneEv(uVar7,local_b0);
      _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_58,uVar7);
      plVar9 = local_50;
      puVar3 = local_58;
      local_58 = (undefined *)0x0;
      local_50 = (long *)0x0;
      plVar12 = *(long **)(param_1 + 0x38);
      *(undefined **)(param_1 + 0x30) = puVar3;
      *(long **)(param_1 + 0x38) = plVar9;
      if (plVar12 != (long *)0x0) {
        plVar9 = plVar12 + 1;
        do {
          iVar11 = (int)*plVar9 + -1;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(plVar9,0x10);
          if (bVar2) {
            *(int *)plVar9 = iVar11;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 == 0) {
          (**(code **)(*plVar12 + 0x10))(plVar12);
          piVar10 = (int *)((long)plVar12 + 0xc);
          do {
            iVar11 = *piVar10;
            cVar1 = '\x01';
            bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
            if (bVar2) {
              *piVar10 = iVar11 + -1;
              cVar1 = ExclusiveMonitorsStatus();
            }
          } while (cVar1 != '\0');
          if (iVar11 + -1 == 0) {
            (**(code **)(*plVar12 + 0x18))(plVar12);
          }
        }
      }
      plVar9 = local_50;
      if (local_50 != (long *)0x0) {
        plVar12 = local_50 + 1;
        do {
          iVar11 = (int)*plVar12 + -1;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
          if (bVar2) {
            *(int *)plVar12 = iVar11;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 == 0) {
          (**(code **)(*local_50 + 0x10))(local_50);
          piVar10 = (int *)((long)plVar9 + 0xc);
          do {
            iVar11 = *piVar10;
            cVar1 = '\x01';
            bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
            if (bVar2) {
              *piVar10 = iVar11 + -1;
              cVar1 = ExclusiveMonitorsStatus();
            }
          } while (cVar1 != '\0');
          if (iVar11 + -1 == 0) {
            (**(code **)(*plVar9 + 0x18))(plVar9);
          }
        }
      }
      if (local_a8 != (long *)0x0) {
        plVar9 = local_a8 + 1;
        do {
          iVar11 = (int)*plVar9 + -1;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(plVar9,0x10);
          if (bVar2) {
            *(int *)plVar9 = iVar11;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
        if (iVar11 == 0) {
          (**(code **)(*local_a8 + 0x10))(local_a8);
          piVar10 = (int *)((long)local_a8 + 0xc);
          do {
            iVar11 = *piVar10;
            cVar1 = '\x01';
            bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
            if (bVar2) {
              *piVar10 = iVar11 + -1;
              cVar1 = ExclusiveMonitorsStatus();
            }
          } while (cVar1 != '\0');
          if (iVar11 + -1 == 0) {
            (**(code **)(*local_a8 + 0x18))(local_a8);
          }
        }
      }
    }
  }
  if ((*(long **)(param_1 + 0x30) != (long *)0x0) &&
     (*(long *)(**(long **)(param_1 + 0x30) + -0x18) != 0)) {
    if (*(long *)(lVar5 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
    return;
  }
  lVar5 = _Znwm(0x10);
  *(long *)lVar5 = lVar5;
  *(long *)(lVar5 + 8) = lVar5;
  _ZN5boost10shared_ptrISt4listISsSaISsEEEC2IS3_EEPT_(&local_c0,lVar5);
  uVar7 = local_c0;
  FUN_0307a6fc(&local_58,"Missing Zone name",&local_80);
  puVar6 = (undefined8 *)_Znwm(0x18);
  *puVar6 = 0;
  puVar6[1] = 0;
  puVar3 = PTR_DAT_03c37adf_1_03bd0478;
  puVar6[2] = local_58;
  local_58 = puVar3 + 0x18;
  FUN_0303d178(puVar6,uVar7);
  if (local_58 + -0x18 != puVar3) {
    piVar10 = (int *)(local_58 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar11 = *piVar10;
      *piVar10 = iVar11 + -1;
    }
    else {
      do {
        iVar11 = *piVar10;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar2) {
          *piVar10 = iVar11 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (iVar11 < 1) {
      _ZdlPv(local_58 + -0x18);
    }
  }
  uVar7 = _Znwm(8);
  FUN_0307a6fc(uVar7,"LoginRequest Error",&local_58);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_d0,uVar7);
  local_e0 = _Znwm(0x48);
  plVar9 = &local_d0;
  local_f0 = local_d0;
  local_e8 = plStack_c8;
  if (plStack_c8 != (long *)0x0) {
    plStack_c8 = plStack_c8 + 1;
    do {
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plStack_c8,0x10);
      if (bVar2) {
        *(int *)plStack_c8 = (int)*plStack_c8 + 1;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
  }
  local_100 = local_c0;
  local_f8 = plStack_b8;
  if (plStack_b8 != (long *)0x0) {
    plVar9 = plStack_b8 + 1;
    do {
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar2) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
  }
  _ZN5Sfs2X10Exceptions18SFSValidationErrorC2EN5boost10shared_ptrISsEENS3_ISt4listISsSaISsEEEE
            (plVar9,local_e0,&local_f0,&local_100);
  uStack_d8 = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions18SFSValidationErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_e0,local_e0,(ulong)&local_e0 | 8);
  plVar9 = local_f8;
  if (local_f8 != (long *)0x0) {
    plVar12 = local_f8 + 1;
    do {
      iVar11 = (int)*plVar12 + -1;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar2) {
        *(int *)plVar12 = iVar11;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
    if (iVar11 == 0) {
      (**(code **)(*local_f8 + 0x10))(local_f8);
      piVar10 = (int *)((long)plVar9 + 0xc);
      do {
        iVar11 = *piVar10;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar2) {
          *piVar10 = iVar11 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_e8;
  if (local_e8 != (long *)0x0) {
    plVar12 = local_e8 + 1;
    do {
      iVar11 = (int)*plVar12 + -1;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar2) {
        *(int *)plVar12 = iVar11;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
    if (iVar11 == 0) {
      (**(code **)(*local_e8 + 0x10))(local_e8);
      piVar10 = (int *)((long)plVar9 + 0xc);
      do {
        iVar11 = *piVar10;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar2) {
          *piVar10 = iVar11 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar11 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  puVar6 = (undefined8 *)__cxa_allocate_exception(0x10);
  uVar7 = uStack_d8;
  puVar6[1] = 0;
  uStack_d8 = 0;
  puVar6[1] = uVar7;
  *puVar6 = local_e0;
  local_e0 = 0;
                    /* WARNING: Subroutine does not return */
  __cxa_throw(puVar6,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEEE_03bd18c8
              ,PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEED2Ev_03bd87c0);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests12LoginRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02a59e08
================================================================

void _ZN5Sfs2X8Requests12LoginRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  long *plVar6;
  size_t sVar7;
  code *pcVar8;
  int *piVar9;
  int iVar10;
  long lVar11;
  undefined8 uVar12;
  long local_170;
  long *local_168;
  undefined8 local_160;
  long *local_158;
  undefined8 local_150;
  long *local_148;
  undefined8 local_140;
  long *local_138;
  undefined8 local_130;
  long *local_128;
  undefined *local_120;
  undefined8 local_118;
  long *local_110;
  undefined8 local_108;
  long *local_100;
  undefined8 local_f8;
  long *local_f0;
  undefined8 local_e8;
  long *local_e0;
  char acStack_d8 [4];
  char acStack_d4 [2];
  char acStack_d2 [2];
  char acStack_d0 [2];
  char acStack_ce [2];
  char acStack_cc [2];
  char acStack_ca [2];
  char acStack_c8 [2];
  char acStack_c6 [2];
  char acStack_c4 [2];
  char acStack_c2 [2];
  char acStack_c0 [2];
  char acStack_be [2];
  char acStack_bc [2];
  char acStack_ba [10];
  long local_b0 [11];
  byte local_58;
  byte local_57;
  byte local_56;
  byte local_55;
  byte local_54;
  byte local_53;
  byte local_52;
  byte local_51;
  byte local_50;
  byte local_4f;
  byte local_4e;
  byte local_4d;
  byte local_4c;
  byte local_4b;
  byte local_4a;
  byte local_49;
  long local_48;
  
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
  plVar6 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar6 + 0x2a8);
  local_e8 = *(undefined8 *)PTR__ZN5Sfs2X8Requests12LoginRequest13KEY_ZONE_NAMEE_03bd1000;
  local_e0 = *(long **)(PTR__ZN5Sfs2X8Requests12LoginRequest13KEY_ZONE_NAMEE_03bd1000 + 8);
  if (local_e0 != (long *)0x0) {
    plVar1 = local_e0 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_f8 = *(undefined8 *)(param_1 + 0x30);
  local_f0 = *(long **)(param_1 + 0x38);
  if (local_f0 != (long *)0x0) {
    plVar1 = local_f0 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar8)(plVar6,&local_e8,&local_f8);
  plVar6 = local_f0;
  if (local_f0 != (long *)0x0) {
    plVar1 = local_f0 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_f0 + 0x10))(local_f0);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = local_e0;
  if (local_e0 != (long *)0x0) {
    plVar1 = local_e0 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_e0 + 0x10))(local_e0);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar6 + 0x2a8);
  local_108 = *(undefined8 *)PTR__ZN5Sfs2X8Requests12LoginRequest13KEY_USER_NAMEE_03bd9160;
  local_100 = *(long **)(PTR__ZN5Sfs2X8Requests12LoginRequest13KEY_USER_NAMEE_03bd9160 + 8);
  if (local_100 != (long *)0x0) {
    plVar1 = local_100 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_118 = *(undefined8 *)(param_1 + 0x40);
  local_110 = *(long **)(param_1 + 0x48);
  if (local_110 != (long *)0x0) {
    plVar1 = local_110 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar8)(plVar6,&local_108,&local_118);
  plVar6 = local_110;
  if (local_110 != (long *)0x0) {
    plVar1 = local_110 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_110 + 0x10))(local_110);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = local_100;
  if (local_100 != (long *)0x0) {
    plVar1 = local_100 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_100 + 0x10))(local_100);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  puVar5 = PTR_DAT_03c37adf_1_03bd0478;
  if ((*(long **)(param_1 + 0x50) != (long *)0x0) &&
     (*(long *)(**(long **)(param_1 + 0x50) + -0x18) != 0)) {
    local_120 = PTR_DAT_03c37adf_1_03bd0478 + 0x18;
    _ZN5Sfs2X8SmartFox12SessionTokenEv(&local_130,*param_2);
    uVar12 = *(undefined8 *)(param_1 + 0x50);
    FUN_0307e06c(local_b0,local_130);
    FUN_0307b158(local_b0,uVar12);
    FUN_0307b718(&local_120,local_b0);
    plVar6 = local_128;
    if ((undefined *)(local_b0[0] + -0x18) != puVar5) {
      piVar9 = (int *)(local_b0[0] + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar10 = *piVar9;
        *piVar9 = iVar10 + -1;
      }
      else {
        do {
          iVar10 = *piVar9;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
          if (bVar3) {
            *piVar9 = iVar10 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      if (iVar10 < 1) {
        _ZdlPv((undefined *)(local_b0[0] + -0x18));
        plVar6 = local_128;
      }
    }
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
      do {
        iVar10 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar10;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 == 0) {
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar9 = (int *)((long)plVar6 + 0xc);
        do {
          iVar10 = *piVar9;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
          if (bVar3) {
            *piVar9 = iVar10 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar10 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    md5_init(local_b0);
    md5_append(local_b0,local_120,*(undefined4 *)(local_120 + -0x18));
    md5_finish(local_b0,&local_58);
    sprintf(acStack_d8,"%02x",(ulong)local_58);
    sprintf((char *)((ulong)acStack_d8 | 2),"%02x",(ulong)local_57);
    sprintf(acStack_d4,"%02x",(ulong)local_56);
    sprintf(acStack_d2,"%02x",(ulong)local_55);
    sprintf(acStack_d0,"%02x",(ulong)local_54);
    sprintf(acStack_ce,"%02x",(ulong)local_53);
    sprintf(acStack_cc,"%02x",(ulong)local_52);
    sprintf(acStack_ca,"%02x",(ulong)local_51);
    sprintf(acStack_c8,"%02x",(ulong)local_50);
    sprintf(acStack_c6,"%02x",(ulong)local_4f);
    sprintf(acStack_c4,"%02x",(ulong)local_4e);
    sprintf(acStack_c2,"%02x",(ulong)local_4d);
    sprintf(acStack_c0,"%02x",(ulong)local_4c);
    sprintf(acStack_be,"%02x",(ulong)local_4b);
    sprintf(acStack_bc,"%02x",(ulong)local_4a);
    sprintf(acStack_ba,"%02x",(ulong)local_49);
    FUN_0307c7fc(*(long **)(param_1 + 0x50),0,*(undefined8 *)(**(long **)(param_1 + 0x50) + -0x18),0
                );
    uVar12 = *(undefined8 *)(param_1 + 0x50);
    sVar7 = strlen(acStack_d8);
    FUN_0307ccd0(uVar12,acStack_d8,sVar7);
    if (local_120 + -0x18 != puVar5) {
      piVar9 = (int *)(local_120 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar10 = *piVar9;
        *piVar9 = iVar10 + -1;
      }
      else {
        do {
          iVar10 = *piVar9;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
          if (bVar3) {
            *piVar9 = iVar10 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      if (iVar10 < 1) {
        _ZdlPv(local_120 + -0x18);
      }
    }
  }
  plVar6 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar6 + 0x2a8);
  local_140 = *(undefined8 *)PTR__ZN5Sfs2X8Requests12LoginRequest12KEY_PASSWORDE_03bce860;
  local_138 = *(long **)(PTR__ZN5Sfs2X8Requests12LoginRequest12KEY_PASSWORDE_03bce860 + 8);
  if (local_138 != (long *)0x0) {
    plVar1 = local_138 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_150 = *(undefined8 *)(param_1 + 0x50);
  local_148 = *(long **)(param_1 + 0x58);
  if (local_148 != (long *)0x0) {
    plVar1 = local_148 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar8)(plVar6,&local_140,&local_150);
  plVar6 = local_148;
  if (local_148 != (long *)0x0) {
    plVar1 = local_148 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_148 + 0x10))(local_148);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = local_138;
  if (local_138 != (long *)0x0) {
    plVar1 = local_138 + 1;
    do {
      iVar10 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar10;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar10 == 0) {
      (**(code **)(*local_138 + 0x10))(local_138);
      piVar9 = (int *)((long)plVar6 + 0xc);
      do {
        iVar10 = *piVar9;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar3) {
          *piVar9 = iVar10 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  lVar11 = *(long *)(param_1 + 0x60);
  if (lVar11 != 0) {
    plVar6 = *(long **)(param_1 + 8);
    pcVar8 = *(code **)(*plVar6 + 0x378);
    local_160 = *(undefined8 *)PTR__ZN5Sfs2X8Requests12LoginRequest10KEY_PARAMSE_03bd5fd0;
    local_158 = *(long **)(PTR__ZN5Sfs2X8Requests12LoginRequest10KEY_PARAMSE_03bd5fd0 + 8);
    if (local_158 != (long *)0x0) {
      plVar1 = local_158 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      lVar11 = *(long *)(param_1 + 0x60);
    }
    local_168 = *(long **)(param_1 + 0x68);
    if (local_168 != (long *)0x0) {
      plVar1 = local_168 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_170 = lVar11;
    (*pcVar8)(plVar6,&local_160,&local_170);
    plVar6 = local_168;
    if (local_168 != (long *)0x0) {
      plVar1 = local_168 + 1;
      do {
        iVar10 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar10;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 == 0) {
        (**(code **)(*local_168 + 0x10))(local_168);
        piVar9 = (int *)((long)plVar6 + 0xc);
        do {
          iVar10 = *piVar9;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
          if (bVar3) {
            *piVar9 = iVar10 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar10 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    plVar6 = local_158;
    if (local_158 != (long *)0x0) {
      plVar1 = local_158 + 1;
      do {
        iVar10 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar10;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar10 == 0) {
        (**(code **)(*local_158 + 0x10))(local_158);
        piVar9 = (int *)((long)plVar6 + 0xc);
        do {
          iVar10 = *piVar9;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar9,0x10);
          if (bVar3) {
            *piVar9 = iVar10 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar10 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8SmartFox20SendHandshakeRequestEb
// ADDRESS : 02a71f40
================================================================

void _ZN5Sfs2X8SmartFox20SendHandshakeRequestEb(long param_1,ulong param_2)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  undefined *puVar7;
  undefined8 uVar8;
  int *piVar9;
  undefined8 local_a0;
  long *plStack_98;
  long local_90;
  undefined1 auStack_88 [8];
  long local_80;
  undefined8 local_78;
  long *local_70;
  long local_68;
  undefined8 local_60;
  long *local_58 [2];
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
  uVar8 = _Znwm(0x30);
  _ZN5Sfs2X8SmartFox7VersionEv(&local_78,param_1);
  FUN_0307e06c(&local_68,local_78);
  if ((param_2 & 1) == 0) {
    FUN_0307a6fc(&local_80,&DAT_0323d65d,auStack_88);
  }
  else {
    FUN_0307e06c(&local_80,*(undefined8 *)(param_1 + 0x78));
  }
  FUN_0307e06c(&local_90,*(undefined8 *)(param_1 + 0x40));
  _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs(uVar8,&local_68,&local_80,&local_90);
  local_58[0] = (long *)0x0;
  local_60 = uVar8;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_60,uVar8,local_58);
  puVar7 = PTR_DAT_03c37adf_1_03bd0478;
  if ((undefined *)(local_90 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar9 = (int *)(local_90 + -8);
    do {
      iVar5 = *piVar9;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 < 1) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a72130 with catch @ 02a721a4
                       catch(type#1 @ 00000000) { ... } // from try @ 02a721b4 with catch @ 02a721a4
                        */
      _ZdlPv((undefined *)(local_90 + -0x18));
    }
  }
  if ((undefined *)(local_80 + -0x18) != puVar7) {
                    /* try { // try from 02a721b0 to 02b721b3 has its CatchHandler @ 02a721b8 */
    piVar9 = (int *)(local_80 + -8);
    do {
                    /* try { // try from 02a721b4 to 02b721b7 has its CatchHandler @ 02a721a4 */
      iVar5 = *piVar9;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a721b0 with catch @ 02a721b8
                        */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
                    /* try { // try from 02a721c4 to 02b721c7 has its CatchHandler @ 02a72060 */
    if (iVar5 < 1) {
      _ZdlPv((undefined *)(local_80 + -0x18));
    }
  }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a71ed4 with catch @ 02a72020
                        */
                    /* try { // try from 02a72028 to 02b7202b has its CatchHandler @ 02a7202c */
                    /* catch() { ... } // from try @ 02a72028 with catch @ 02a7202c */
  if ((undefined *)(local_68 + -0x18) != puVar7) {
    piVar9 = (int *)(local_68 + -8);
    do {
      iVar5 = *piVar9;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
      if (bVar4) {
        *piVar9 = iVar5 + -1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 < 1) {
      _ZdlPv((undefined *)(local_68 + -0x18));
    }
  }
  if (local_70 != (long *)0x0) {
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
                    /* try { // try from 02a7204c to 02b7204f has its CatchHandler @ 02a72050 */
    if (iVar5 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a7204c with catch @ 02a72050
                        */
                    /* try { // try from 02a7205c to 02b7205f has its CatchHandler @ 02a71e70 */
      (**(code **)(*local_70 + 0x10))(local_70);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02a720fc with catch @ 02a72060
                       catch(type#1 @ 00000000) { ... } // from try @ 02a7217c with catch @ 02a72060
                       catch(type#1 @ 00000000) { ... } // from try @ 02a721c4 with catch @ 02a72060
                        */
      piVar9 = (int *)((long)local_70 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  plVar1 = local_58[0];
  local_a0 = local_60;
  plStack_98 = local_58[0];
  if (local_58[0] != (long *)0x0) {
    plVar2 = local_58[0] + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  _ZN5Sfs2X8SmartFox4SendEN5boost10shared_ptrINS_8Requests8IRequestEEE(param_1,&local_a0);
  if (plVar1 != (long *)0x0) {
    plVar2 = plVar1 + 1;
    do {
      iVar5 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar1 + 0x10))(plVar1);
      piVar9 = (int *)((long)plVar1 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02a720fc to 02b720ff has its CatchHandler @ 02a72060 */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  plVar1 = local_58[0];
  if (local_58[0] != (long *)0x0) {
    plVar2 = local_58[0] + 1;
    do {
      iVar5 = (int)*plVar2 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar4) {
        *(int *)plVar2 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02a72130 to 02b72157 has its CatchHandler @ 02a721a4 */
      (**(code **)(*local_58[0] + 0x10))(local_58[0]);
      piVar9 = (int *)((long)plVar1 + 0xc);
      do {
        iVar5 = *piVar9;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar9,0x10);
        if (bVar4) {
          *piVar9 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02a7217c to 02b7217f has its CatchHandler @ 02a72060 */
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12SFSIOHandlerES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02a844f8
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12SFSIOHandlerES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEEE_03bda460;
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  if (param_2 != 0) {
    _ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0_
              (param_2 + 8,param_1,param_2);
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEED0Ev  [thunk -> 0x302e670]
// ADDRESS : 02a845f4
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZdlPv(void *__ptr)

{
  (*(code *)PTR_free_03bc3f18)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE7disposeEv
// ADDRESS : 02a845f8
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE7disposeEv(long param_1)

{
  if (*(long **)(param_1 + 0x10) != (long *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x02a84608. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(**(long **)(param_1 + 0x10) + 0x28))();
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE11get_deleterERKSt9type_info
// ADDRESS : 02a84610
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE11get_deleterERKSt9type_info(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE17get_local_deleterERKSt9type_info
// ADDRESS : 02a84618
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE19get_untyped_deleterEv
// ADDRESS : 02a84620
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12SFSIOHandlerEE19get_untyped_deleterEv(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0_
// ADDRESS : 02a84628
================================================================

void _ZNK5boost23enable_shared_from_thisIN5Sfs2X4Core12SFSIOHandlerEE22_internal_accept_ownerIS3_S3_EEvPKNS_10shared_ptrIT_EEPT0_
               (undefined8 *param_1,long param_2,undefined8 param_3)

{
  int *piVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  long *plVar5;
  long *plVar6;
  
  if ((param_1[1] == 0) || (*(int *)(param_1[1] + 8) == 0)) {
    plVar6 = *(long **)(param_2 + 8);
    if (plVar6 != (long *)0x0) {
      plVar5 = plVar6 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar5,0x10);
        if (bVar4) {
          *(int *)plVar5 = (int)*plVar5 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plVar5 = (long *)param_1[1];
    *param_1 = param_3;
    if (plVar6 != plVar5) {
      if (plVar6 != (long *)0x0) {
        piVar1 = (int *)((long)plVar6 + 0xc);
        do {
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = *piVar1 + 1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        plVar5 = (long *)param_1[1];
      }
      if (plVar5 != (long *)0x0) {
        piVar1 = (int *)((long)plVar5 + 0xc);
        do {
          iVar2 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar2 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar2 + -1 == 0) {
          (**(code **)(*plVar5 + 0x18))(plVar5);
        }
      }
      param_1[1] = plVar6;
    }
    if (plVar6 != (long *)0x0) {
      plVar5 = plVar6 + 1;
      do {
        iVar2 = (int)*plVar5 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar5,0x10);
        if (bVar4) {
          *(int *)plVar5 = iVar2;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar2 == 0) {
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar1 = (int *)((long)plVar6 + 0xc);
        do {
          iVar2 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar2 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar2 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02a86e5c
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Requests16HandshakeRequestES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEEE_03bd1be0;
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,param_2,param_2);
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEED0Ev
// ADDRESS : 02a86f44
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEED0Ev(void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE7disposeEv
// ADDRESS : 02a86f48
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE7disposeEv
               (long param_1)

{
  if (*(long **)(param_1 + 0x10) != (long *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x02a86f58. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(**(long **)(param_1 + 0x10) + 0x40))();
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE11get_deleterERKSt9type_info
// ADDRESS : 02a86f60
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE11get_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE17get_local_deleterERKSt9type_info
// ADDRESS : 02a86f68
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE19get_untyped_deleterEv
// ADDRESS : 02a86f70
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X8Requests16HandshakeRequestEE19get_untyped_deleterEv
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util9CryptoKeyES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02abc0e4
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util9CryptoKeyES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEEE_03bd80b0;
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
                    /* try { // try from 02abc144 to 02bbc147 has its CatchHandler @ 02abc1c0 */
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,param_2,param_2);
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEED0Ev
// ADDRESS : 02abc27c
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEED0Ev(void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE7disposeEv
// ADDRESS : 02abc280
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE7disposeEv(long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  void *__ptr;
  long *plVar6;
  
  __ptr = *(void **)(param_1 + 0x10);
  if (__ptr != (void *)0x0) {
    plVar6 = *(long **)((long)__ptr + 0x18);
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
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
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
        do {
          iVar5 = *piVar2;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02abc2d4 to 02bbc2d7 has its CatchHandler @ 02abc76c */
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    plVar6 = *(long **)((long)__ptr + 8);
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
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
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
        do {
          iVar5 = *piVar2;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02abc330 to 02bbc3bf has its CatchHandler @ 02abc1f0 */
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    _ZdlPv(__ptr);
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE11get_deleterERKSt9type_info
// ADDRESS : 02abc368
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE11get_deleterERKSt9type_info(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE17get_local_deleterERKSt9type_info
// ADDRESS : 02abc370
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE17get_local_deleterERKSt9type_info(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE19get_untyped_deleterEv
// ADDRESS : 02abc378
================================================================

undefined8 _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util9CryptoKeyEE19get_untyped_deleterEv(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKeyC1EN5boost10shared_ptrINS0_9ByteArrayEEES5_
// ADDRESS : 02abc814
================================================================

void _ZN5Sfs2X4Util9CryptoKeyC1EN5boost10shared_ptrINS0_9ByteArrayEEES5_
               (undefined8 *param_1,undefined8 *param_2,undefined8 *param_3)

{
  int *piVar1;
  long *plVar2;
  undefined8 uVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  long *plVar8;
  
                    /* try { // try from 02abc824 to 02bbc827 has its CatchHandler @ 02abc8ac */
  param_1[1] = 0;
  *param_1 = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  uVar3 = *param_2;
  lVar4 = param_2[1];
  if (lVar4 == 0) {
    *param_1 = uVar3;
    param_1[1] = 0;
  }
  else {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    plVar8 = (long *)param_1[1];
    *param_1 = uVar3;
    param_1[1] = lVar4;
    if (plVar8 != (long *)0x0) {
      plVar2 = plVar8 + 1;
      do {
        iVar7 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*plVar8 + 0x10))(plVar8);
        piVar1 = (int *)((long)plVar8 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
                    /* catch() { ... } // from try @ 02abc824 with catch @ 02abc8ac */
        }
      }
    }
  }
  uVar3 = *param_3;
  lVar4 = param_3[1];
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  plVar8 = (long *)param_1[3];
                    /* try { // try from 02abc8d4 to 02bbc8d7 has its CatchHandler @ 02abc7d0 */
  param_1[2] = uVar3;
  param_1[3] = lVar4;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02abc9c8 with catch @ 02abc8d8
                       catch(type#1 @ 00000000) { ... } // from try @ 02abc9f8 with catch @ 02abc8d8
                       catch(type#1 @ 00000000) { ... } // from try @ 02abca20 with catch @ 02abc8d8
                        */
  if (plVar8 != (long *)0x0) {
    plVar2 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKey2IVEv
// ADDRESS : 02abc944
================================================================

void _ZN5Sfs2X4Util9CryptoKey2IVEv(undefined8 *param_1,undefined8 *param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *param_2;
  lVar4 = param_2[1];
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Util9CryptoKey3KeyEv
// ADDRESS : 02abc970
================================================================

void _ZN5Sfs2X4Util9CryptoKey3KeyEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *(undefined8 *)(param_2 + 0x10);
  lVar4 = *(long *)(param_2 + 0x18);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv
// ADDRESS : 02ad0d80
================================================================

void _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
                    /* try { // try from 02ad0d80 to 02bd0d83 has its CatchHandler @ 02ad0d20 */
                    /* catch() { ... } // from try @ 02ad0de4 with catch @ 02ad0d84 */
  *param_1 = *(undefined8 *)(param_2 + 0x170);
  lVar4 = *(long *)(param_2 + 0x178);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEN5boost10shared_ptrINS_4Util9CryptoKeyEEE
// ADDRESS : 02ad0dac
================================================================

void _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEN5boost10shared_ptrINS_4Util9CryptoKeyEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  long *plVar2;
  undefined8 uVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  long *plVar8;
  
  uVar3 = *param_2;
  lVar4 = param_2[1];
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  plVar8 = *(long **)(param_1 + 0x178);
  *(undefined8 *)(param_1 + 0x170) = uVar3;
  *(long *)(param_1 + 0x178) = lVar4;
  if (plVar8 != (long *)0x0) {
    plVar2 = plVar8 + 1;
    do {
                    /* try { // try from 02ad0de4 to 02bd0de7 has its CatchHandler @ 02ad0d84 */
                    /* catch() { ... } // from try @ 02ad0e48 with catch @ 02ad0de8 */
      iVar7 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_
// ADDRESS : 02ae5d34
================================================================

void _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_
               (undefined8 *param_1,long param_2)

{
  undefined *puVar1;
  long *plVar2;
  
  *param_1 = 0;
  plVar2 = (long *)_Znwm(0x18);
  puVar1 = 
  PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEEE_03bd5d70;
  plVar2[1] = 0x100000001;
  plVar2[2] = param_2;
  *plVar2 = (long)(puVar1 + 0x10);
  *param_1 = plVar2;
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEED0Ev
// ADDRESS : 02ae5e10
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEED0Ev(void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE7disposeEv
// ADDRESS : 02ae5e14
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE7disposeEv
               (long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *__ptr;
  long *plVar6;
  
  __ptr = *(long **)(param_1 + 0x10);
  if (__ptr != (long *)0x0) {
    plVar6 = (long *)__ptr[2];
    *__ptr = (long)(PTR__ZTVN5Sfs2X4Core22DefaultPacketEncrypterE_03bd3de0 + 0x10);
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
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
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
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
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
    _ZdlPv(__ptr);
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE11get_deleterERKSt9type_info
// ADDRESS : 02ae5eb0
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE11get_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE17get_local_deleterERKSt9type_info
// ADDRESS : 02ae5eb8
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE19get_untyped_deleterEv
// ADDRESS : 02ae5ec0
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core22DefaultPacketEncrypterEE19get_untyped_deleterEv
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5Sfs2X11Controllers16SystemController11FnHandshakeEyN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 02aed7c8
================================================================

void _ZN5Sfs2X11Controllers16SystemController11FnHandshakeEyN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (long param_1,undefined8 *param_2)

{
  undefined *puVar1;
  long *plVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  long lVar6;
  uint uVar7;
  long lVar8;
  long lVar9;
  undefined8 uVar10;
  long lVar11;
  ulong uVar12;
  int *piVar13;
  int iVar14;
  undefined8 *puVar15;
  size_t __n;
  undefined1 auVar16 [16];
  undefined *local_d0;
  long *local_c8;
  undefined *local_c0;
  long *local_b8;
  long local_b0;
  long *local_a8;
  undefined8 local_a0;
  long *local_98;
  long *local_90;
  long *plStack_88;
  undefined *local_80;
  long *plStack_78;
  long *plStack_70;
  long local_60;
  long *local_58;
  undefined1 auStack_50 [8];
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
  lVar8 = _Znwm(0x30);
  *(undefined8 *)(lVar8 + 0x10) = 0;
  *(undefined8 *)(lVar8 + 0x18) = 0;
  *(undefined8 *)(lVar8 + 0x20) = 0;
  *(undefined8 *)(lVar8 + 0x28) = 0;
  puVar15 = (undefined8 *)(lVar8 + 8);
  *puVar15 = 0;
  *(undefined8 **)(lVar8 + 0x18) = puVar15;
  *(undefined8 **)(lVar8 + 0x20) = puVar15;
  _ZN5boost10shared_ptrISt3mapISsNS0_IvEESt4lessISsESaISt4pairIKSsS2_EEEEC2IS9_EEPT_
            (&local_60,lVar8);
  lVar8 = local_60;
  (**(code **)(*(long *)*param_2 + 0x10))(&local_90);
  FUN_0307a6fc(&local_80,"message",auStack_50);
  plStack_70 = plStack_88;
  plStack_78 = local_90;
  local_90 = (long *)0x0;
  plStack_88 = (long *)0x0;
  auVar16 = FUN_027b61f4(lVar8,&local_80);
  lVar11 = auVar16._8_8_;
  if (lVar11 != 0) {
    if ((auVar16._0_8_ == 0) && (lVar8 + 8 != lVar11)) {
      uVar12 = *(ulong *)(local_80 + -0x18);
      __n = *(ulong *)((long)*(void **)(lVar11 + 0x20) + -0x18);
      lVar9 = uVar12 - __n;
      if (uVar12 < __n || lVar9 == 0) {
        __n = uVar12;
      }
      uVar7 = memcmp(local_80,*(void **)(lVar11 + 0x20),__n);
      uVar12 = (ulong)uVar7;
      if ((uVar7 == 0) && (uVar12 = 0, lVar9 < 0x80000000)) {
        uVar7 = (uint)lVar9;
        if (lVar9 < -0x7fffffff) {
          uVar7 = 0x80000000;
        }
        uVar12 = (ulong)uVar7;
      }
      uVar12 = uVar12 >> 0x1f;
    }
    else {
      uVar12 = 1;
    }
    lVar9 = _Znwm(0x38);
    plVar2 = plStack_70;
    plVar3 = plStack_78;
    puVar1 = PTR_DAT_03c37adf_1_03bd0478 + 0x18;
    plStack_78 = (long *)0x0;
    plStack_70 = (long *)0x0;
    *(long **)(lVar9 + 0x28) = plVar3;
    *(undefined **)(lVar9 + 0x20) = local_80;
    *(long **)(lVar9 + 0x30) = plVar2;
    local_80 = puVar1;
    FUN_0306006c(uVar12,lVar9,lVar11,lVar8 + 8);
    *(long *)(lVar8 + 0x28) = *(long *)(lVar8 + 0x28) + 1;
  }
  plVar3 = plStack_70;
  if (plStack_70 != (long *)0x0) {
    plVar2 = plStack_70 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*plStack_70 + 0x10))(plStack_70);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  plVar3 = plStack_88;
  if (local_80 + -0x18 != PTR_DAT_03c37adf_1_03bd0478) {
    piVar13 = (int *)(local_80 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar14 = *piVar13;
      *piVar13 = iVar14 + -1;
    }
    else {
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    if (iVar14 < 1) {
      _ZdlPv(local_80 + -0x18);
      plVar3 = plStack_88;
    }
  }
  plStack_88 = plVar3;
  if (plVar3 != (long *)0x0) {
    plVar2 = plVar3 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*plVar3 + 0x10))(plVar3);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  uVar10 = _Znwm(0x30);
  local_a0 = *(undefined8 *)PTR__ZN5Sfs2X4Core8SFSEvent9HANDSHAKEE_03bd2b08;
  local_98 = *(long **)(PTR__ZN5Sfs2X4Core8SFSEvent9HANDSHAKEE_03bd2b08 + 8);
  if (local_98 != (long *)0x0) {
    plVar3 = local_98 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = (int)*plVar3 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  local_b0 = local_60;
  local_a8 = local_58;
  if (local_58 != (long *)0x0) {
    plVar3 = local_58 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = (int)*plVar3 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X4Core8SFSEventC1EN5boost10shared_ptrISsEENS3_ISt3mapISsNS3_IvEESt4lessISsESaISt4pairIKSsS6_EEEEE
            (uVar10,&local_a0,&local_b0);
  _ZN5boost10shared_ptrIN5Sfs2X4Core8SFSEventEEC2IS3_EEPT_(&local_80,uVar10);
  plVar3 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar2 = local_a8 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  plVar3 = local_98;
  if (local_98 != (long *)0x0) {
    plVar2 = local_98 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  uVar10 = *(undefined8 *)(param_1 + 0x10);
  local_c0 = local_80;
  local_b8 = plStack_78;
  if (plStack_78 != (long *)0x0) {
    plVar3 = plStack_78 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = (int)*plVar3 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X8SmartFox15HandleHandShakeEN5boost10shared_ptrINS_4Core9BaseEventEEE(uVar10,&local_c0);
  plVar3 = local_b8;
  if (local_b8 != (long *)0x0) {
    plVar2 = local_b8 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*local_b8 + 0x10))(local_b8);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  uVar10 = *(undefined8 *)(param_1 + 0x10);
  local_d0 = local_80;
  local_c8 = plStack_78;
  if (plStack_78 != (long *)0x0) {
    plVar3 = plStack_78 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = (int)*plVar3 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X8SmartFox13DispatchEventEN5boost10shared_ptrINS_4Core9BaseEventEEE(uVar10,&local_d0);
  plVar3 = local_c8;
  if (local_c8 != (long *)0x0) {
    plVar2 = local_c8 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  plVar3 = plStack_78;
  if (plStack_78 != (long *)0x0) {
    plVar2 = plStack_78 + 1;
    do {
      iVar14 = (int)*plVar2 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*plStack_78 + 0x10))(plStack_78);
      piVar13 = (int *)((long)plVar3 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  if (local_58 != (long *)0x0) {
    plVar3 = local_58 + 1;
    do {
      iVar14 = (int)*plVar3 + -1;
                    /* catch() { ... } // from try @ 02aedcd8 with catch @ 02aedc78 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar14;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar14 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar13 = (int *)((long)local_58 + 0xc);
      do {
        iVar14 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar14 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar14 + -1 == 0) {
        (**(code **)(*local_58 + 0x18))(local_58);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02aedcd8 to 02bedcdb has its CatchHandler @ 02aedc78 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
// ADDRESS : 02b38d7c
================================================================

void _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
               (long *param_1,long *param_2)

{
  int *piVar1;
  long *plVar2;
  long lVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  undefined *puVar8;
  long *plVar9;
  
  puVar8 = PTR__ZTVN5Sfs2X4Core22DefaultPacketEncrypterE_03bd3de0;
  param_1[1] = 0;
  param_1[2] = 0;
                    /* try { // try from 02b38d98 to 02c38e57 has its CatchHandler @ 02b38b04 */
  *param_1 = (long)(puVar8 + 0x10);
  lVar3 = *param_2;
  lVar4 = param_2[1];
  if (lVar4 == 0) {
                    /* catch() { ... } // from try @ 02b38bb4 with catch @ 02b38e18 */
    param_1[1] = lVar3;
    param_1[2] = 0;
  }
  else {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar6) {
        *piVar1 = *piVar1 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    plVar9 = (long *)param_1[2];
    param_1[1] = lVar3;
    param_1[2] = lVar4;
    if (plVar9 != (long *)0x0) {
      plVar2 = plVar9 + 1;
      do {
        iVar7 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b38d68 with catch @ 02b38e10 */
          (**(code **)(*plVar9 + 0x18))(plVar9);
                    /* catch() { ... } // from try @ 02b38cf8 with catch @ 02b38e14 */
        }
      }
    }
  }
                    /* catch() { ... } // from try @ 02b38be8 with catch @ 02b38e1c */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core22DefaultPacketEncrypter7EncryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b38e2c
================================================================

void _ZN5Sfs2X4Core22DefaultPacketEncrypter7EncryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  long lVar6;
  int iVar7;
  EVP_CIPHER_CTX *ctx;
  undefined8 uVar8;
  undefined8 *puVar9;
  long lVar10;
  long lVar11;
  EVP_CIPHER *cipher;
  ulong uVar12;
  ulong uVar13;
  uchar *puVar14;
  uchar *in;
  undefined1 local_f8 [8];
  long *local_f0;
  int local_e4;
  undefined8 *local_e0;
  long *local_d8;
  int local_cc;
  undefined8 local_c8;
  long *local_c0;
  undefined8 *local_b8;
  long *local_b0;
  undefined8 local_a8;
  long *local_a0;
  undefined8 *local_98;
  long *local_90;
  long *local_88;
  long *local_80;
  undefined1 auStack_78 [8];
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
                    /* catch() { ... } // from try @ 02b38c14 with catch @ 02b38e2c */
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02b38e58 to 02c38e87 has its CatchHandler @ 02b38f48 */
  _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv(&local_58,*(undefined8 *)(param_1 + 8));
  ctx = EVP_CIPHER_CTX_new();
  EVP_CIPHER_CTX_reset(ctx);
  uVar8 = _Znwm(0x890);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_78,*param_2);
  _ZN5Sfs2X4Util9ByteArrayC1EN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar8,auStack_78);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_68,uVar8);
  if (local_70 != (long *)0x0) {
    plVar1 = local_70 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02b38ec8 to 02c38ef7 has its CatchHandler @ 02b38f4c */
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar2 = (int *)((long)local_70 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  puVar9 = (undefined8 *)_Znwm(0x18);
  puVar9[1] = 0;
  puVar9[2] = 0;
  *puVar9 = 0;
  _ZN5boost10shared_ptrISt6vectorIhSaIhEEEC2IS3_EEPT_(&local_88,puVar9);
  lVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_68);
  lVar11 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_68);
                    /* catch() { ... } // from try @ 02b38e58 with catch @ 02b38f48 */
                    /* catch() { ... } // from try @ 02b38ec8 with catch @ 02b38f4c */
                    /* catch() { ... } // from try @ 02b38b6c with catch @ 02b38f50 */
  uVar12 = (lVar10 + 0x10) - lVar11 % 0x10;
  uVar13 = local_88[1] - *local_88;
  if (uVar12 < uVar13 || uVar12 - uVar13 == 0) {
    if (uVar12 < uVar13) {
      local_88[1] = *local_88 + uVar12;
    }
  }
  else {
    _ZNSt6vectorIhSaIhEE17_M_default_appendEm(local_88,uVar12 - uVar13);
  }
                    /* try { // try from 02b38f7c to 02c38fab has its CatchHandler @ 02b38fc8 */
  cipher = EVP_aes_128_cbc();
  _ZN5Sfs2X4Util9CryptoKey3KeyEv(&local_a8,local_58);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_98,local_a8);
  puVar14 = (uchar *)*local_98;
                    /* try { // try from 02b38fac to 02c38fcb has its CatchHandler @ 02b38b04 */
  _ZN5Sfs2X4Util9CryptoKey2IVEv(&local_c8,local_58);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_b8,local_c8);
                    /* catch() { ... } // from try @ 02b38f7c with catch @ 02b38fc8 */
                    /* try { // try from 02b38fcc to 02c3902f has its CatchHandler @ 02b38fcc
                       catch() { ... } // from try @ 02b38fcc with catch @ 02b38fcc
                       catch() { ... } // from try @ 02b39098 with catch @ 02b38fcc
                       catch() { ... } // from try @ 02b3917c with catch @ 02b38fcc */
  EVP_CipherInit_ex(ctx,cipher,(ENGINE *)0x0,puVar14,(uchar *)*local_b8,1);
  if (local_b0 != (long *)0x0) {
    plVar1 = local_b0 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar2 = (int *)((long)local_b0 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b39030 to 02c3903f has its CatchHandler @ 02b39120 */
        (**(code **)(*local_b0 + 0x18))(local_b0);
      }
    }
  }
  if (local_c0 != (long *)0x0) {
    plVar1 = local_c0 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_c0 + 0x10))(local_c0);
      piVar2 = (int *)((long)local_c0 + 0xc);
      do {
                    /* try { // try from 02b39068 to 02c39097 has its CatchHandler @ 02b3911c */
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_c0 + 0x18))(local_c0);
      }
    }
  }
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
                    /* try { // try from 02b39098 to 02c3914b has its CatchHandler @ 02b38fcc */
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar2 = (int *)((long)local_90 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_90 + 0x18))(local_90);
      }
    }
  }
  if (local_a0 != (long *)0x0) {
    plVar1 = local_a0 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_a0 + 0x10))(local_a0);
      piVar2 = (int *)((long)local_a0 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* catch() { ... } // from try @ 02b39068 with catch @ 02b3911c */
                    /* catch() { ... } // from try @ 02b39030 with catch @ 02b39120 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_a0 + 0x18))(local_a0);
      }
    }
  }
  local_cc = 0;
  puVar14 = (uchar *)*local_88;
                    /* try { // try from 02b3914c to 02c3917b has its CatchHandler @ 02b391e4 */
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_e0,local_68);
  in = (uchar *)*local_e0;
  iVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_68);
  EVP_CipherUpdate(ctx,puVar14,&local_cc,in,iVar7);
                    /* try { // try from 02b3917c to 02c391e7 has its CatchHandler @ 02b38fcc */
  if (local_d8 != (long *)0x0) {
    plVar1 = local_d8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar2 = (int *)((long)local_d8 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_d8 + 0x18))(local_d8);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3914c with catch @ 02b391e4 */
  EVP_CipherFinal_ex(ctx,(uchar *)(*local_88 + (long)local_cc),&local_e4);
  uVar12 = (long)local_cc + (long)local_e4;
  local_cc = (int)uVar12;
  uVar13 = local_88[1] - *local_88;
  if (uVar13 < uVar12) {
    _ZNSt6vectorIhSaIhEE17_M_default_appendEm(local_88,uVar12 - uVar13);
  }
  else if (uVar13 != uVar12) {
    local_88[1] = *local_88 + uVar12;
  }
                    /* try { // try from 02b39230 to 02c39267 has its CatchHandler @ 02b39230
                       catch() { ... } // from try @ 02b39230 with catch @ 02b39230
                       catch() { ... } // from try @ 02b39274 with catch @ 02b39230 */
  uVar8 = *param_2;
  local_f0 = local_80;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X4Util9ByteArray5BytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar8,local_f8);
  plVar1 = local_f0;
  if (local_f0 != (long *)0x0) {
                    /* try { // try from 02b39268 to 02c39273 has its CatchHandler @ 02b392f8 */
    plVar3 = local_f0 + 1;
    do {
      iVar7 = (int)*plVar3 + -1;
                    /* try { // try from 02b39274 to 02c39367 has its CatchHandler @ 02b39230 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_f0 + 0x10))(local_f0);
      piVar2 = (int *)((long)plVar1 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  EVP_CIPHER_CTX_free(ctx);
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar2 = (int *)((long)local_80 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* catch() { ... } // from try @ 02b39268 with catch @ 02b392f8 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)local_60 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_60 + 0x18))(local_60);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3947c with catch @ 02b39374
                       catch() { ... } // from try @ 02b394f4 with catch @ 02b39374 */
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)local_50 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_50 + 0x18))(local_50);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_48) {
                    /* try { // try from 02b393e0 to 02c393eb has its CatchHandler @ 02b39498 */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core22DefaultPacketEncrypter7DecryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b39844
================================================================

void _ZN5Sfs2X4Core22DefaultPacketEncrypter7DecryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  long lVar6;
  int iVar7;
  EVP_CIPHER_CTX *ctx;
  undefined8 uVar8;
  undefined8 *puVar9;
  ulong uVar10;
  EVP_CIPHER *cipher;
  ulong uVar11;
  uchar *puVar12;
  uchar *in;
  undefined1 local_f8 [8];
  long *local_f0;
  int local_e4;
  undefined8 *local_e0;
  long *local_d8;
  int local_cc;
  undefined8 local_c8;
  long *local_c0;
  undefined8 *local_b8;
  long *local_b0;
  undefined8 local_a8;
  long *local_a0;
  undefined8 *local_98;
  long *local_90;
  long *local_88;
  long *local_80;
  undefined1 auStack_78 [8];
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02b3986c to 02c3986f has its CatchHandler @ 02b39944 */
  _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv(&local_58,*(undefined8 *)(param_1 + 8));
  ctx = EVP_CIPHER_CTX_new();
  EVP_CIPHER_CTX_reset(ctx);
  uVar8 = _Znwm(0x890);
                    /* try { // try from 02b39894 to 02c39897 has its CatchHandler @ 02b3993c */
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_78,*param_2);
  _ZN5Sfs2X4Util9ByteArrayC1EN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar8,auStack_78);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_68,uVar8);
  if (local_70 != (long *)0x0) {
    plVar1 = local_70 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02b398ec to 02c3990f has its CatchHandler @ 02b39958 */
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar2 = (int *)((long)local_70 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b39910 to 02c39973 has its CatchHandler @ 02b39824 */
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  puVar9 = (undefined8 *)_Znwm(0x18);
  puVar9[1] = 0;
  puVar9[2] = 0;
  *puVar9 = 0;
  _ZN5boost10shared_ptrISt6vectorIhSaIhEEEC2IS3_EEPT_(&local_88,puVar9);
                    /* catch() { ... } // from try @ 02b39894 with catch @ 02b3993c */
  uVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_68);
                    /* catch() { ... } // from try @ 02b3986c with catch @ 02b39944 */
  uVar11 = local_88[1] - *local_88;
  if (uVar10 < uVar11 || uVar10 - uVar11 == 0) {
    if (uVar10 < uVar11) {
      local_88[1] = *local_88 + uVar10;
    }
  }
  else {
                    /* catch() { ... } // from try @ 02b398ec with catch @ 02b39958 */
    _ZNSt6vectorIhSaIhEE17_M_default_appendEm(local_88,uVar10 - uVar11);
  }
  cipher = EVP_aes_128_cbc();
                    /* try { // try from 02b39974 to 02c39977 has its CatchHandler @ 02b39990 */
                    /* try { // try from 02b39978 to 02c39993 has its CatchHandler @ 02b39824 */
  _ZN5Sfs2X4Util9CryptoKey3KeyEv(&local_a8,local_58);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_98,local_a8);
                    /* catch() { ... } // from try @ 02b39974 with catch @ 02b39990 */
  puVar12 = (uchar *)*local_98;
  _ZN5Sfs2X4Util9CryptoKey2IVEv(&local_c8,local_58);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_b8,local_c8);
                    /* try { // try from 02b399c4 to 02c399c7 has its CatchHandler @ 02b399e0 */
  EVP_CipherInit_ex(ctx,cipher,(ENGINE *)0x0,puVar12,(uchar *)*local_b8,0);
  if (local_b0 != (long *)0x0) {
    plVar1 = local_b0 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b399c4 with catch @ 02b399e0
                        */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b399e4 to 02c39a2f has its CatchHandler @ 02b399e4
                       catch() { ... } // from try @ 02b399e4 with catch @ 02b399e4
                       catch() { ... } // from try @ 02b39aa0 with catch @ 02b399e4 */
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar2 = (int *)((long)local_b0 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_b0 + 0x18))(local_b0);
      }
    }
  }
  if (local_c0 != (long *)0x0) {
    plVar1 = local_c0 + 1;
    do {
                    /* try { // try from 02b39a30 to 02c39a33 has its CatchHandler @ 02b39ae0 */
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_c0 + 0x10))(local_c0);
      piVar2 = (int *)((long)local_c0 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* try { // try from 02b39a5c to 02c39a5f has its CatchHandler @ 02b39ab4 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_c0 + 0x18))(local_c0);
      }
    }
  }
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b39a98 to 02c39a9f has its CatchHandler @ 02b39ac4 */
    if (iVar7 == 0) {
                    /* try { // try from 02b39aa0 to 02c39afb has its CatchHandler @ 02b399e4 */
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar2 = (int *)((long)local_90 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* catch() { ... } // from try @ 02b39a5c with catch @ 02b39ab4 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b39a98 with catch @ 02b39ac4 */
        (**(code **)(*local_90 + 0x18))(local_90);
      }
    }
  }
  if (local_a0 != (long *)0x0) {
    plVar1 = local_a0 + 1;
    do {
                    /* catch() { ... } // from try @ 02b39a30 with catch @ 02b39ae0 */
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02b39afc to 02c39b17 has its CatchHandler @ 02b39afc
                       catch() { ... } // from try @ 02b39afc with catch @ 02b39afc
                       catch() { ... } // from try @ 02b39b20 with catch @ 02b39afc */
      (**(code **)(*local_a0 + 0x10))(local_a0);
      piVar2 = (int *)((long)local_a0 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b39b18 to 02c39b1f has its CatchHandler @ 02b39b38 */
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b39b20 to 02c39b4b has its CatchHandler @ 02b39afc */
        (**(code **)(*local_a0 + 0x18))(local_a0);
      }
    }
  }
  local_cc = 0;
                    /* catch() { ... } // from try @ 02b39b18 with catch @ 02b39b38 */
  puVar12 = (uchar *)*local_88;
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_e0,local_68);
  in = (uchar *)*local_e0;
  iVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_68);
  EVP_CipherUpdate(ctx,puVar12,&local_cc,in,iVar7);
  if (local_d8 != (long *)0x0) {
    plVar1 = local_d8 + 1;
    do {
                    /* try { // try from 02b39b7c to 02c39b7f has its CatchHandler @ 02b39ba0 */
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar2 = (int *)((long)local_d8 + 0xc);
      do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b39b7c with catch @ 02b39ba0
                        */
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_d8 + 0x18))(local_d8);
      }
    }
  }
                    /* try { // try from 02b39bd8 to 02c39bdb has its CatchHandler @ 02b39bf4 */
  EVP_CipherFinal_ex(ctx,(uchar *)(*local_88 + (long)local_cc),&local_e4);
  uVar10 = (long)local_cc + (long)local_e4;
  local_cc = (int)uVar10;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b39bd8 with catch @ 02b39bf4
                        */
  uVar11 = local_88[1] - *local_88;
  if (uVar11 < uVar10) {
    _ZNSt6vectorIhSaIhEE17_M_default_appendEm(local_88,uVar10 - uVar11);
  }
  else if (uVar11 != uVar10) {
    local_88[1] = *local_88 + uVar10;
  }
  uVar8 = *param_2;
  local_f0 = local_80;
                    /* try { // try from 02b39c2c to 02c39c2f has its CatchHandler @ 02b39c50 */
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X4Util9ByteArray5BytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar8,local_f8);
  plVar1 = local_f0;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b39c2c with catch @ 02b39c50
                        */
  if (local_f0 != (long *)0x0) {
    plVar3 = local_f0 + 1;
    do {
      iVar7 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_f0 + 0x10))(local_f0);
      piVar2 = (int *)((long)plVar1 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* try { // try from 02b39c88 to 02c39c8b has its CatchHandler @ 02b39ca4 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b39c88 with catch @ 02b39ca4
                        */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  EVP_CIPHER_CTX_free(ctx);
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02b39cdc to 02c39cdf has its CatchHandler @ 02b39d00 */
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar2 = (int *)((long)local_80 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b39cdc with catch @ 02b39d00
                        */
                    /* catch() { ... } // from try @ 02b39d74 with catch @ 02b39d04 */
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)local_60 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b39d48 to 02c39d4b has its CatchHandler @ 02b39dcc */
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_60 + 0x18))(local_60);
      }
    }
  }
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
                    /* try { // try from 02b39d70 to 02c39d73 has its CatchHandler @ 02b39db8 */
      iVar7 = (int)*plVar1 + -1;
                    /* try { // try from 02b39d74 to 02c39ddf has its CatchHandler @ 02b39d04 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar7;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)local_50 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar7 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_50 + 0x18))(local_50);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b39d70 with catch @ 02b39db8 */
  if (*(long *)(lVar6 + 0x28) == local_48) {
                    /* catch() { ... } // from try @ 02b39d48 with catch @ 02b39dcc */
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* catch() { ... } // from try @ 02b39e78 with catch @ 02b39de0
                       catch() { ... } // from try @ 02b39ed0 with catch @ 02b39de0 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandlerC2EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
// ADDRESS : 02b3a754
================================================================

void _ZN5Sfs2X4Core12SFSIOHandlerC2EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
               (long *param_1,long *param_2)

{
  undefined *puVar1;
  int *piVar2;
  long lVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 uVar8;
  long lVar9;
  long *plVar10;
  long *plVar11;
  long local_70;
  long *local_68;
  long local_60;
  long *local_58;
  long *plStack_50;
  long local_48;
  
  lVar7 = tpidr_el0;
  local_48 = *(long *)(lVar7 + 0x28);
                    /* try { // try from 02b3a780 to 02c3a78f has its CatchHandler @ 02b3b364 */
  puVar1 = PTR__ZTVN5Sfs2X4Core12SFSIOHandlerE_03bd1598 + 0x10;
  param_1[1] = 0;
  param_1[2] = 0;
  *param_1 = (long)puVar1;
  memset(param_1 + 3,0,0x78);
                    /* try { // try from 02b3a7a8 to 02c3a7cb has its CatchHandler @ 02b3b5b4 */
  uVar8 = _Znwm(0x890);
  _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar8);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_60,uVar8);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
                    /* try { // try from 02b3a7cc to 02c3a7d7 has its CatchHandler @ 02b3b2fc */
  plVar10 = (long *)param_1[4];
  param_1[3] = lVar9;
  param_1[4] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3a810 to 02c3a83f has its CatchHandler @ 02b3b274 */
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b3a854 to 02c3a863 has its CatchHandler @ 02b3b35c */
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3a87c to 02c3a89f has its CatchHandler @ 02b3b4f0 */
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  lVar9 = *param_2;
  lVar3 = param_2[1];
  if (lVar3 != 0) {
    piVar2 = (int *)(lVar3 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
      if (bVar5) {
        *piVar2 = *piVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  plVar11 = (long *)param_1[6];
                    /* try { // try from 02b3a8a0 to 02c3a8ab has its CatchHandler @ 02b3b288 */
  param_1[5] = lVar9;
  param_1[6] = lVar3;
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b3a8e4 to 02c3a913 has its CatchHandler @ 02b3b26c */
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  _ZN5Sfs2X8Bitswarm14BitSwarmClient3LogEv(&local_60,*param_2);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
  plVar10 = (long *)param_1[8];
  param_1[7] = lVar9;
  param_1[8] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
                    /* try { // try from 02b3a91c to 02c3a92b has its CatchHandler @ 02b3b360 */
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
                    /* try { // try from 02b3a940 to 02c3a963 has its CatchHandler @ 02b3b678 */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3a964 to 02c3a96f has its CatchHandler @ 02b3b2c4 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3a9a8 to 02c3a9d7 has its CatchHandler @ 02b3b270 */
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  lVar9 = _Znwm(0x18);
  local_70 = *param_2;
  local_68 = (long *)param_2[1];
                    /* try { // try from 02b3a9dc to 02c3a9fb has its CatchHandler @ 02b3b4dc */
  if (local_68 != (long *)0x0) {
    plVar11 = local_68 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b3a9fc to 02c3aa07 has its CatchHandler @ 02b3b34c */
  _ZN5Sfs2X4Core22DefaultPacketEncrypterC1EN5boost10shared_ptrINS_8Bitswarm14BitSwarmClientEEE
            (lVar9,&local_70);
  local_58 = (long *)0x0;
  local_60 = lVar9;
                    /* try { // try from 02b3aa08 to 02c3aa17 has its CatchHandler @ 02b3b334 */
  _ZN5boost6detail12shared_countC2IN5Sfs2X4Core22DefaultPacketEncrypterEEEPT_(&plStack_50,lVar9);
  plVar11 = local_58;
  local_58 = plStack_50;
  plStack_50 = plVar11;
                    /* try { // try from 02b3aa18 to 02c3aa23 has its CatchHandler @ 02b3b2c0 */
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
                    /* try { // try from 02b3aa74 to 02c3aab7 has its CatchHandler @ 02b3b368 */
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_60,lVar9,lVar9);
  plVar11 = local_58;
  lVar9 = local_60;
  local_60 = 0;
  local_58 = (long *)0x0;
  plVar10 = (long *)param_1[0x11];
  param_1[0x10] = lVar9;
  param_1[0x11] = (long)plVar11;
  if (plVar10 != (long *)0x0) {
    plVar11 = plVar10 + 1;
    do {
      iVar6 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar10 = local_58 + 1;
    do {
                    /* try { // try from 02b3aaf0 to 02c3ab1f has its CatchHandler @ 02b3b268 */
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_68;
  if (local_68 != (long *)0x0) {
    plVar10 = local_68 + 1;
    do {
                    /* try { // try from 02b3ab44 to 02c3ab73 has its CatchHandler @ 02b3b264 */
      iVar6 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_68 + 0x10))(local_68);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b3ab7c to 02c3ab7f has its CatchHandler @ 02b3b278 */
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = (long *)param_1[10];
  param_1[9] = 0;
  param_1[10] = 0;
  if (plVar11 != (long *)0x0) {
    plVar10 = plVar11 + 1;
    do {
      iVar6 = (int)*plVar10 + -1;
                    /* try { // try from 02b3aba8 to 02c3abd7 has its CatchHandler @ 02b3b260 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv(param_1);
                    /* try { // try from 02b3ac00 to 02c3ac2f has its CatchHandler @ 02b3b25c */
  if (*(long *)(lVar7 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv
// ADDRESS : 02b3b010
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler10InitStatesEv(long param_1)

{
  int *piVar1;
  ulong uVar2;
  ulong uVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  void *__ptr;
  void *pvVar8;
  size_t __n;
  long *plVar9;
  ulong uVar10;
  long **pplVar11;
  long *plVar12;
  long lVar13;
  void *local_88;
  long *local_80;
  long *local_78;
  long *local_70;
  long local_68;
  
                    /* try { // try from 02b3b02c to 02c3b05b has its CatchHandler @ 02b3b060 */
  lVar7 = tpidr_el0;
  local_68 = *(long *)(lVar7 + 0x28);
  pvVar8 = (void *)_Znwm(0x38);
  _ZN5Sfs2X3FSM18FiniteStateMachineC2Ev();
  local_80 = (long *)0x0;
  local_88 = pvVar8;
  _ZN5boost6detail12shared_countC2IN5Sfs2X3FSM18FiniteStateMachineEEEPT_(&local_70,pvVar8);
  plVar9 = local_80;
                    /* catch() { ... } // from try @ 02b3b02c with catch @ 02b3b060 */
                    /* catch() { ... } // from try @ 02b3adb0 with catch @ 02b3b064 */
                    /* catch() { ... } // from try @ 02b3ad9c with catch @ 02b3b068 */
  local_80 = local_70;
                    /* catch() { ... } // from try @ 02b3ad90 with catch @ 02b3b06c */
  local_70 = plVar9;
                    /* catch() { ... } // from try @ 02b3ae3c with catch @ 02b3b070 */
  if (plVar9 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b3ad48 with catch @ 02b3b074 */
    plVar12 = plVar9 + 1;
    do {
      iVar6 = (int)*plVar12 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar5) {
        *(int *)plVar12 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
                    /* try { // try from 02b3b0a0 to 02c3b0cf has its CatchHandler @ 02b3b0d4 */
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_88,pvVar8,pvVar8);
  plVar9 = local_80;
  pvVar8 = local_88;
                    /* catch() { ... } // from try @ 02b3b0a0 with catch @ 02b3b0d4 */
                    /* catch() { ... } // from try @ 02b3acc8 with catch @ 02b3b0d8 */
  local_88 = (void *)0x0;
  local_80 = (long *)0x0;
  plVar12 = *(long **)(param_1 + 0x78);
  *(void **)(param_1 + 0x70) = pvVar8;
  *(long **)(param_1 + 0x78) = plVar9;
  if (plVar12 != (long *)0x0) {
    plVar9 = plVar12 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b3b108 to 02c3b13b has its CatchHandler @ 02b3b14c */
      (**(code **)(*plVar12 + 0x10))(plVar12);
      piVar1 = (int *)((long)plVar12 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar12 + 0x18))(plVar12);
      }
    }
  }
  plVar9 = local_80;
  if (local_80 != (long *)0x0) {
    plVar12 = local_80 + 1;
    do {
      iVar6 = (int)*plVar12 + -1;
                    /* catch() { ... } // from try @ 02b3b108 with catch @ 02b3b14c */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar5) {
        *(int *)plVar12 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* catch() { ... } // from try @ 02b3acb0 with catch @ 02b3b150 */
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3b180 to 02c3b1af has its CatchHandler @ 02b3b1c8 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  lVar13 = 0;
  local_88 = (void *)0x0;
  local_80 = (long *)0x0;
  local_78 = (long *)0x0;
  do {
    uVar10 = (long)local_80 - (long)local_88 >> 3;
    uVar3 = uVar10;
    if (uVar10 == 0) {
      uVar3 = 1;
    }
                    /* try { // try from 02b3b200 to 02c3b22f has its CatchHandler @ 02b3b234 */
    uVar2 = 0x1fffffffffffffff;
    if (!CARRY8(uVar3,uVar10) && uVar3 + uVar10 >> 0x3d == 0) {
      uVar2 = uVar3 + uVar10;
    }
    if (uVar2 == 0) {
                    /* catch() { ... } // from try @ 02b3b200 with catch @ 02b3b234 */
                    /* catch() { ... } // from try @ 02b3ac70 with catch @ 02b3b238 */
      pvVar8 = (void *)0x0;
    }
    else {
      if (uVar2 >> 0x3d != 0) {
                    /* WARNING: Subroutine does not return */
                    /* catch() { ... } // from try @ 02b3aa74 with catch @ 02b3b368 */
        FUN_03078b34();
      }
      pvVar8 = (void *)_Znwm(uVar2 << 3);
    }
    __ptr = local_88;
                    /* catch() { ... } // from try @ 02b3ac5c with catch @ 02b3b23c */
    __n = (long)local_80 - (long)local_88;
    *(long *)((long)pvVar8 + __n) = lVar13;
    if ((long)__n >> 3 != 0) {
                    /* catch() { ... } // from try @ 02b3ac50 with catch @ 02b3b254 */
                    /* catch() { ... } // from try @ 02b3acfc with catch @ 02b3b258 */
      memmove(pvVar8,local_88,__n);
    }
                    /* catch() { ... } // from try @ 02b3ac00 with catch @ 02b3b25c */
                    /* catch() { ... } // from try @ 02b3aba8 with catch @ 02b3b260 */
    if (__ptr != (void *)0x0) {
                    /* catch() { ... } // from try @ 02b3ab44 with catch @ 02b3b264 */
                    /* catch() { ... } // from try @ 02b3aaf0 with catch @ 02b3b268 */
      _ZdlPv(__ptr);
    }
                    /* catch() { ... } // from try @ 02b3a8e4 with catch @ 02b3b26c */
    plVar9 = (long *)((long)pvVar8 + uVar2 * 8);
                    /* catch() { ... } // from try @ 02b3a9a8 with catch @ 02b3b270 */
                    /* catch() { ... } // from try @ 02b3a810 with catch @ 02b3b274 */
                    /* catch() { ... } // from try @ 02b3ab7c with catch @ 02b3b278 */
    pplVar11 = &local_78;
    local_80 = (long *)((long)pvVar8 + __n) + 1;
    while( true ) {
      *pplVar11 = plVar9;
      local_88 = pvVar8;
      if (3 < lVar13) {
                    /* catch() { ... } // from try @ 02b3a8a0 with catch @ 02b3b288 */
        _ZN5Sfs2X3FSM18FiniteStateMachine12AddAllStatesERSt6vectorIlSaIlEE
                  (*(undefined8 *)(param_1 + 0x70),&local_88);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),0,1,0);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),1,3,1);
                    /* catch() { ... } // from try @ 02b3aa18 with catch @ 02b3b2c0 */
                    /* catch() { ... } // from try @ 02b3a964 with catch @ 02b3b2c4 */
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),1,2,2);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),2,3,3);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),3,0,4);
                    /* catch() { ... } // from try @ 02b3a7cc with catch @ 02b3b2fc */
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),3,4,5);
        _ZN5Sfs2X3FSM18FiniteStateMachine18AddStateTransitionElll
                  (*(undefined8 *)(param_1 + 0x70),4,0,6);
        _ZN5Sfs2X3FSM18FiniteStateMachine15SetCurrentStateEl(*(undefined8 *)(param_1 + 0x70),0);
        if (local_88 != (void *)0x0) {
                    /* catch() { ... } // from try @ 02b3aa08 with catch @ 02b3b334 */
          _ZdlPv(local_88);
        }
        if (*(long *)(lVar7 + 0x28) != local_68) {
                    /* WARNING: Subroutine does not return */
          __stack_chk_fail();
        }
                    /* catch() { ... } // from try @ 02b3a9fc with catch @ 02b3b34c */
                    /* catch() { ... } // from try @ 02b3a854 with catch @ 02b3b35c */
                    /* catch() { ... } // from try @ 02b3a91c with catch @ 02b3b360 */
                    /* catch() { ... } // from try @ 02b3a780 with catch @ 02b3b364 */
        return;
      }
                    /* catch() { ... } // from try @ 02b3b180 with catch @ 02b3b1c8 */
      lVar13 = lVar13 + 1;
                    /* catch() { ... } // from try @ 02b3ac7c with catch @ 02b3b1cc */
      if (local_80 == local_78) break;
      plVar9 = local_80 + 1;
      *local_80 = lVar13;
      pplVar11 = &local_80;
    }
  } while( true );
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler7DisposeEv
// ADDRESS : 02b3b40c
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler7DisposeEv(long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  if (*(long *)(param_1 + 0x28) != 0) {
    plVar6 = *(long **)(param_1 + 0x30);
    *(undefined8 *)(param_1 + 0x28) = 0;
    *(undefined8 *)(param_1 + 0x30) = 0;
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
      do {
        iVar5 = (int)*plVar1 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3b440 to 02c3b46f has its CatchHandler @ 02b3b4d4 */
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
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
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
  }
  if (*(long *)(param_1 + 0x38) != 0) {
    _ZN5Sfs2X7Logging6Logger7DisposeEv();
    plVar6 = *(long **)(param_1 + 0x40);
    *(undefined8 *)(param_1 + 0x38) = 0;
    *(undefined8 *)(param_1 + 0x40) = 0;
    if (plVar6 != (long *)0x0) {
                    /* try { // try from 02b3b498 to 02c3b4c7 has its CatchHandler @ 02b3b4d8 */
      plVar1 = plVar6 + 1;
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
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
        do {
          iVar5 = *piVar2;
                    /* catch() { ... } // from try @ 02b3b3e8 with catch @ 02b3b4cc */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* catch() { ... } // from try @ 02b3b390 with catch @ 02b3b4d0 */
        } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3b440 with catch @ 02b3b4d4 */
        if (iVar5 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3b498 with catch @ 02b3b4d8 */
                    /* catch() { ... } // from try @ 02b3a9dc with catch @ 02b3b4dc */
                    /* catch() { ... } // from try @ 02b3a750 with catch @ 02b3b4e0 */
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
  }
  if (*(long *)(param_1 + 0x58) != 0) {
                    /* catch() { ... } // from try @ 02b3a87c with catch @ 02b3b4f0 */
    plVar6 = *(long **)(param_1 + 0x60);
    *(undefined8 *)(param_1 + 0x58) = 0;
    *(undefined8 *)(param_1 + 0x60) = 0;
    if (plVar6 != (long *)0x0) {
      plVar1 = plVar6 + 1;
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
        (**(code **)(*plVar6 + 0x10))(plVar6);
        piVar2 = (int *)((long)plVar6 + 0xc);
        do {
          iVar5 = *piVar2;
                    /* try { // try from 02b3b52c to 02c3b55b has its CatchHandler @ 02b3b5b0 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar6 + 0x18))(plVar6);
        }
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandlerD2Ev
// ADDRESS : 02b3b564
================================================================

void _ZN5Sfs2X4Core12SFSIOHandlerD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[0x11];
  *param_1 = (long)(PTR__ZTVN5Sfs2X4Core12SFSIOHandlerE_03bd1598 + 0x10);
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* catch() { ... } // from try @ 02b3b52c with catch @ 02b3b5b0 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
                    /* catch() { ... } // from try @ 02b3a7a8 with catch @ 02b3b5b4 */
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xf];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
                    /* try { // try from 02b3b5f0 to 02c3b61f has its CatchHandler @ 02b3b674 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[0xc];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b3b5f0 with catch @ 02b3b674 */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3a940 with catch @ 02b3b678 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[10];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* try { // try from 02b3b6b4 to 02c3b6e3 has its CatchHandler @ 02b3b794 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[8];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
                    /* try { // try from 02b3b70c to 02c3b73b has its CatchHandler @ 02b3b798 */
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* try { // try from 02b3b73c to 02c3b79b has its CatchHandler @ 02b3a5e0 */
  plVar6 = (long *)param_1[6];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3b6b4 with catch @ 02b3b794 */
  plVar6 = (long *)param_1[4];
                    /* catch() { ... } // from try @ 02b3b70c with catch @ 02b3b798 */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
                    /* try { // try from 02b3b7e0 to 02c3b80f has its CatchHandler @ 02b3b81c */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[2];
  if (plVar6 != (long *)0x0) {
    piVar2 = (int *)((long)plVar6 + 0xc);
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
      (**(code **)(*plVar6 + 0x18))();
    }
  }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3b7e0 with catch @ 02b3b81c
                        */
                    /* try { // try from 02b3b820 to 02c3b893 has its CatchHandler @ 02b3b820
                       catch() { ... } // from try @ 02b3b820 with catch @ 02b3b820
                       catch() { ... } // from try @ 02b3bad4 with catch @ 02b3b820
                       catch() { ... } // from try @ 02b3bd28 with catch @ 02b3b820 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandlerD0Ev
// ADDRESS : 02b3b844
================================================================

void _ZN5Sfs2X4Core12SFSIOHandlerD0Ev(void *param_1)

{
  _ZN5Sfs2X4Core12SFSIOHandlerD2Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler10InitializeEv
// ADDRESS : 02b3b868
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler10InitializeEv(long param_1)

{
  int *piVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  int iVar8;
  long *plVar9;
  undefined8 local_70;
  long *local_68;
  undefined8 local_60;
  long *local_58;
  undefined8 local_50;
  long *local_48;
  undefined *local_40;
  long local_38;
  
  lVar5 = tpidr_el0;
  local_38 = *(long *)(lVar5 + 0x28);
  uVar6 = _Znwm(0x38);
                    /* try { // try from 02b3b894 to 02c3b8af has its CatchHandler @ 02b3bccc */
  plVar7 = *(long **)(param_1 + 0x10);
  if (plVar7 == (long *)0x0) {
LAB_02b3babc:
                    /* try { // try from 02b3bac4 to 02c3bad3 has its CatchHandler @ 02b3bb5c */
    local_40 = PTR__ZTVN5boost12bad_weak_ptrE_03bcea60 + 0x10;
    _ZN5boost15throw_exceptionINS_12bad_weak_ptrEEEvRKT_(&local_40);
  }
  else {
    plVar9 = plVar7 + 1;
    iVar8 = (int)plVar7[1];
    do {
      while( true ) {
        if (iVar8 == 0) goto LAB_02b3babc;
        iVar2 = (int)*plVar9;
                    /* try { // try from 02b3b8bc to 02c3b8cf has its CatchHandler @ 02b3bb34 */
        if (iVar2 == iVar8) break;
        ClearExclusiveLocal();
                    /* try { // try from 02b3b8b0 to 02c3b8bb has its CatchHandler @ 02b3bb4c */
        iVar8 = iVar2;
      }
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar8 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3b8d0 to 02c3b8db has its CatchHandler @ 02b3bb30 */
      iVar8 = iVar2;
    } while (cVar3 != '\0');
    local_60 = *(undefined8 *)(param_1 + 8);
    local_70 = *(undefined8 *)(param_1 + 0x28);
    local_68 = *(long **)(param_1 + 0x30);
    if (local_68 != (long *)0x0) {
      plVar9 = local_68 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = (int)*plVar9 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    local_58 = plVar7;
    _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
              (uVar6,&local_60,&local_70);
    local_48 = (long *)0x0;
                    /* try { // try from 02b3b920 to 02c3b94f has its CatchHandler @ 02b3bb5c */
    local_50 = uVar6;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_50,uVar6,&local_48);
    plVar7 = local_48;
    uVar6 = local_50;
    local_50 = 0;
    local_48 = (long *)0x0;
    plVar9 = *(long **)(param_1 + 0x60);
    *(undefined8 *)(param_1 + 0x58) = uVar6;
    *(long **)(param_1 + 0x60) = plVar7;
    if (plVar9 != (long *)0x0) {
      plVar7 = plVar9 + 1;
      do {
        iVar8 = (int)*plVar7 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar7,0x10);
        if (bVar4) {
          *(int *)plVar7 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar8 = *piVar1;
                    /* try { // try from 02b3b974 to 02c3b9a3 has its CatchHandler @ 02b3bb1c */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
    plVar7 = local_48;
    if (local_48 != (long *)0x0) {
      plVar9 = local_48 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_48 + 0x10))(local_48);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
                    /* try { // try from 02b3b9c8 to 02c3b9f7 has its CatchHandler @ 02b3bb18 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_68;
    if (local_68 != (long *)0x0) {
      plVar9 = local_68 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3ba00 to 02c3ba03 has its CatchHandler @ 02b3bb20 */
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_68 + 0x10))(local_68);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3ba2c to 02c3ba5b has its CatchHandler @ 02b3bb14 */
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_58;
    if (local_58 != (long *)0x0) {
      plVar9 = local_58 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_58 + 0x10))(local_58);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar8 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3ba84 to 02c3bab3 has its CatchHandler @ 02b3bb10 */
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    if (*(long *)(lVar5 + 0x28) == local_38) {
      return;
    }
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b3bad4 to 02c3bb83 has its CatchHandler @ 02b3b820 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler5CodecEv
// ADDRESS : 02b3bc44
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler5CodecEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *(undefined8 *)(param_2 + 0x58);
  lVar4 = *(long *)(param_2 + 0x60);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler9ReadStateEv
// ADDRESS : 02b3bc70
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler9ReadStateEv(long param_1)

{
  _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv(*(undefined8 *)(param_1 + 0x70));
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler10OnDataReadEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b3bc88
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler10OnDataReadEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,long *param_2)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  int iVar6;
  long lVar7;
  ulong uVar8;
  undefined8 *puVar9;
  undefined8 uVar10;
  int *piVar11;
  long *plVar12;
  long local_128;
  long *local_120;
  long local_118;
  long *local_110;
  long local_108;
  long *local_100;
  long local_f8;
  long *local_f0;
  long local_e8;
  long *local_e0;
  long local_d8;
  long *local_d0;
  long local_c8;
  long *local_c0;
  undefined8 local_b8;
  long *local_b0;
  long local_a8;
  long *local_a0;
  undefined1 auStack_98 [8];
  undefined8 local_90;
  long *local_88;
  long local_80;
  long *local_78;
  undefined *local_70;
  undefined8 uStack_68;
  long local_60;
  long *local_58;
  long local_48;
  
                    /* try { // try from 02b3bc88 to 02c3bcb7 has its CatchHandler @ 02b3bcc8 */
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
                    /* catch() { ... } // from try @ 02b3bbd8 with catch @ 02b3bcbc */
  lVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_2);
                    /* catch() { ... } // from try @ 02b3bb84 with catch @ 02b3bcc0 */
  if (lVar7 == 0) {
    uVar10 = _Znwm(8);
    FUN_0307a6fc(uVar10,"Unexpected empty packet data: no readable bytes available!",&local_70);
                    /* try { // try from 02b3bdd0 to 02c3be1f has its CatchHandler @ 02b3bd34 */
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_60,uVar10);
    local_70 = (undefined *)_Znwm(0x38);
    local_80 = local_60;
    local_78 = local_58;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3bda0 with catch @ 02b3bdf4
                        */
    if (local_58 != (long *)0x0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3bd70 with catch @ 02b3bdf8
                        */
      local_58 = local_58 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(local_58,0x10);
        if (bVar3) {
          *(int *)local_58 = (int)*local_58 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X10Exceptions8SFSErrorC1EN5boost10shared_ptrISsEE(local_70,&local_80);
    uStack_68 = 0;
                    /* try { // try from 02b3be20 to 02c3be4f has its CatchHandler @ 02b3be58 */
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions8SFSErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_70,local_70,(ulong)&local_70 | 8);
    plVar1 = local_78;
    if (local_78 != (long *)0x0) {
      plVar12 = local_78 + 1;
      do {
        iVar6 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar6;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar6 == 0) {
                    /* try { // try from 02b3be50 to 02c3be5b has its CatchHandler @ 02b3bd34 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3be20 with catch @ 02b3be58
                        */
                    /* try { // try from 02b3be5c to 02c3bebb has its CatchHandler @ 02b3be5c
                       catch() { ... } // from try @ 02b3be5c with catch @ 02b3be5c
                       catch() { ... } // from try @ 02b3d2b0 with catch @ 02b3be5c
                       catch() { ... } // from try @ 02b3ddf4 with catch @ 02b3be5c */
        (**(code **)(*local_78 + 0x10))(local_78);
        piVar11 = (int *)((long)plVar1 + 0xc);
        do {
          iVar6 = *piVar11;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
          if (bVar3) {
            *piVar11 = iVar6 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
    puVar9 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar10 = uStack_68;
    puVar9[1] = 0;
    uStack_68 = 0;
    puVar9[1] = uVar10;
    *puVar9 = local_70;
    local_70 = (undefined *)0x0;
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar9,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions8SFSErrorEEE_03bd5a38,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions8SFSErrorEED2Ev_03bd4130);
  }
                    /* catch() { ... } // from try @ 02b3bc30 with catch @ 02b3bcc4 */
                    /* catch() { ... } // from try @ 02b3bc88 with catch @ 02b3bcc8 */
  if (*(long *)(param_1 + 0x28) != 0) {
                    /* catch() { ... } // from try @ 02b3b894 with catch @ 02b3bccc */
    _ZN5Sfs2X8Bitswarm14BitSwarmClient3SfsEv(&local_90);
    uVar8 = _ZN5Sfs2X8SmartFox5DebugEv(local_90);
    if (local_88 != (long *)0x0) {
      plVar1 = local_88 + 1;
      do {
        iVar6 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar6;
          cVar2 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3bcf8 to 02c3bd27 has its CatchHandler @ 02b3bd30 */
      } while (cVar2 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar11 = (int *)((long)local_88 + 0xc);
        do {
          iVar6 = *piVar11;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
          if (bVar3) {
            *piVar11 = iVar6 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3bd28 to 02c3bd33 has its CatchHandler @ 02b3b820 */
                    /* catch() { ... } // from try @ 02b3bcf8 with catch @ 02b3bd30 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3bdd0 with catch @ 02b3bd34
                       catch(type#1 @ 00000000) { ... } // from try @ 02b3be50 with catch @ 02b3bd34
                        */
          (**(code **)(*local_88 + 0x18))(local_88);
        }
      }
    }
    if ((uVar8 & 1) != 0) {
      lVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_2);
      if (lVar7 < 0x401) {
                    /* try { // try from 02b3bebc to 02c3bed7 has its CatchHandler @ 02b3d668 */
        puVar9 = (undefined8 *)_Znwm(0x18);
        puVar9[1] = 0;
        puVar9[2] = 0;
        *puVar9 = 0;
        _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_60,puVar9);
        lVar7 = local_60;
                    /* try { // try from 02b3bed8 to 02c3bee3 has its CatchHandler @ 02b3d658 */
                    /* try { // try from 02b3bee4 to 02c3bef7 has its CatchHandler @ 02b3d640 */
        FUN_0307a6fc(&local_70,"Data Read: ",auStack_98);
        puVar5 = PTR_DAT_03c37adf_1_03bd0478;
        puVar9 = *(undefined8 **)(lVar7 + 8);
                    /* try { // try from 02b3bef8 to 02c3bf03 has its CatchHandler @ 02b3d63c */
        if (puVar9 == *(undefined8 **)(lVar7 + 0x10)) {
          _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJSsEEEvDpOT_(lVar7,&local_70);
        }
        else {
          *puVar9 = local_70;
          local_70 = puVar5 + 0x18;
          *(undefined8 **)(lVar7 + 8) = puVar9 + 1;
        }
                    /* try { // try from 02b3c038 to 02c3c06f has its CatchHandler @ 02b3d730 */
        if (local_70 + -0x18 != PTR_DAT_03c37adf_1_03bd0478) {
          piVar11 = (int *)(local_70 + -8);
          if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
            iVar6 = *piVar11;
                    /* try { // try from 02b3c9d8 to 02c3c9eb has its CatchHandler @ 02b3d76c */
            *piVar11 = iVar6 + -1;
          }
          else {
            do {
              iVar6 = *piVar11;
                    /* try { // try from 02b3c9a4 to 02c3c9cb has its CatchHandler @ 02b3da04 */
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
          }
          if (iVar6 < 1) {
            _ZdlPv(local_70 + -0x18);
                    /* try { // try from 02b3c9ec to 02c3c9f7 has its CatchHandler @ 02b3d760 */
          }
        }
        lVar7 = local_60;
        local_c8 = *param_2;
        local_c0 = (long *)param_2[1];
        if (local_c0 != (long *)0x0) {
          plVar1 = local_c0 + 1;
          do {
                    /* try { // try from 02b3c070 to 02c3c083 has its CatchHandler @ 02b3d510 */
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
            if (bVar3) {
              *(int *)plVar1 = (int)*plVar1 + 1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
        }
        _ZN5Sfs2X8Protocol13Serialization26DefaultObjectDumpFormatter7HexDumpEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                  (&local_b8,&local_c8);
                    /* try { // try from 02b3c084 to 02c3c08f has its CatchHandler @ 02b3d50c */
        if (*(long *)(lVar7 + 8) == *(long *)(lVar7 + 0x10)) {
          _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(lVar7,local_b8);
          plVar1 = local_b0;
        }
        else {
          FUN_0307e06c();
          *(long *)(lVar7 + 8) = *(long *)(lVar7 + 8) + 8;
          plVar1 = local_b0;
        }
        if (plVar1 != (long *)0x0) {
          plVar12 = plVar1 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
                    /* try { // try from 02b3c0d4 to 02c3c103 has its CatchHandler @ 02b3d528 */
          if (iVar6 == 0) {
            (**(code **)(*plVar1 + 0x10))(plVar1);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
        plVar1 = local_c0;
        if (local_c0 != (long *)0x0) {
          plVar12 = local_c0 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
                    /* try { // try from 02b3c128 to 02c3c157 has its CatchHandler @ 02b3d4e8 */
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*local_c0 + 0x10))(local_c0);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
        uVar10 = *(undefined8 *)(param_1 + 0x38);
        local_d8 = local_60;
        local_d0 = local_58;
        if (local_58 != (long *)0x0) {
          plVar1 = local_58 + 1;
          do {
                    /* try { // try from 02b3c17c to 02c3c1ab has its CatchHandler @ 02b3d4e4 */
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
            if (bVar3) {
              *(int *)plVar1 = (int)*plVar1 + 1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
        }
        _ZN5Sfs2X7Logging6Logger4InfoEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar10,&local_d8);
        plVar1 = local_d0;
        if (local_d0 != (long *)0x0) {
          plVar12 = local_d0 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
                    /* try { // try from 02b3c1b4 to 02c3c1b7 has its CatchHandler @ 02b3d4fc */
            (**(code **)(*local_d0 + 0x10))(local_d0);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c1e0 to 02c3c20f has its CatchHandler @ 02b3d4e0 */
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
        plVar1 = local_58;
        if (local_58 != (long *)0x0) {
          plVar12 = local_58 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*local_58 + 0x10))(local_58);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c238 to 02c3c267 has its CatchHandler @ 02b3d4f0 */
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
      }
      else {
        puVar9 = (undefined8 *)_Znwm(0x18);
        puVar9[1] = 0;
        puVar9[2] = 0;
        *puVar9 = 0;
        _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_60,puVar9);
        lVar7 = local_60;
                    /* try { // try from 02b3bd70 to 02c3bd7b has its CatchHandler @ 02b3bdf8 */
        FUN_0307a6fc(&local_70,"Data Read: Size > 1024, dump omitted",auStack_98);
        puVar5 = PTR_DAT_03c37adf_1_03bd0478;
        puVar9 = *(undefined8 **)(lVar7 + 8);
        if (puVar9 == *(undefined8 **)(lVar7 + 0x10)) {
          _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJSsEEEvDpOT_(lVar7,&local_70);
        }
        else {
          *puVar9 = local_70;
                    /* try { // try from 02b3bda0 to 02c3bdcf has its CatchHandler @ 02b3bdf4 */
          local_70 = puVar5 + 0x18;
          *(undefined8 **)(lVar7 + 8) = puVar9 + 1;
        }
        if (local_70 + -0x18 != PTR_DAT_03c37adf_1_03bd0478) {
                    /* try { // try from 02b3c96c to 02c3c99b has its CatchHandler @ 02b3d758 */
          piVar11 = (int *)(local_70 + -8);
          if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
            iVar6 = *piVar11;
            *piVar11 = iVar6 + -1;
          }
          else {
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
          }
          if (iVar6 < 1) {
            _ZdlPv(local_70 + -0x18);
                    /* try { // try from 02b3c9cc to 02c3c9d7 has its CatchHandler @ 02b3d77c */
          }
        }
                    /* try { // try from 02b3bf40 to 02c3bf87 has its CatchHandler @ 02b3d678 */
        uVar10 = *(undefined8 *)(param_1 + 0x38);
        local_a8 = local_60;
        local_a0 = local_58;
        if (local_58 != (long *)0x0) {
          plVar1 = local_58 + 1;
          do {
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
            if (bVar3) {
              *(int *)plVar1 = (int)*plVar1 + 1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
        }
        _ZN5Sfs2X7Logging6Logger4InfoEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar10,&local_a8);
        plVar1 = local_a0;
        if (local_a0 != (long *)0x0) {
          plVar12 = local_a0 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*local_a0 + 0x10))(local_a0);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
                    /* try { // try from 02b3bfac to 02c3bfdb has its CatchHandler @ 02b3d4f8 */
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
        plVar1 = local_58;
        if (local_58 != (long *)0x0) {
          plVar12 = local_58 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*local_58 + 0x10))(local_58);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
                    /* try { // try from 02b3c000 to 02c3c02f has its CatchHandler @ 02b3d4f4 */
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
      }
    }
  }
  _ZN5Sfs2X4Util9ByteArray8PositionEl(*param_2,0);
  lVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_2);
  while (0 < lVar7) {
    iVar6 = _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv(*(undefined8 *)(param_1 + 0x70));
    if (iVar6 == 0) {
      local_e8 = *param_2;
      local_e0 = (long *)param_2[1];
      if (local_e0 != (long *)0x0) {
        plVar1 = local_e0 + 1;
        do {
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
          if (bVar3) {
            *(int *)plVar1 = (int)*plVar1 + 1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      _ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                (&local_60,param_1,&local_e8);
      plVar1 = local_58;
      lVar7 = local_60;
      local_60 = 0;
      local_58 = (long *)0x0;
      plVar12 = (long *)param_2[1];
      *param_2 = lVar7;
      param_2[1] = (long)plVar1;
      if (plVar12 != (long *)0x0) {
                    /* try { // try from 02b3c410 to 02c3c417 has its CatchHandler @ 02b3db30 */
        plVar1 = plVar12 + 1;
        do {
          iVar6 = (int)*plVar1 + -1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
          if (bVar3) {
            *(int *)plVar1 = iVar6;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar6 == 0) {
                    /* try { // try from 02b3c430 to 02c3c43b has its CatchHandler @ 02b3d9ec */
          (**(code **)(*plVar12 + 0x10))(plVar12);
          piVar11 = (int *)((long)plVar12 + 0xc);
          do {
                    /* try { // try from 02b3c43c to 02c3c44b has its CatchHandler @ 02b3d9cc */
            iVar6 = *piVar11;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
            if (bVar3) {
              *piVar11 = iVar6 + -1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
                    /* try { // try from 02b3c44c to 02c3c457 has its CatchHandler @ 02b3d9c8 */
          if (iVar6 + -1 == 0) {
            (**(code **)(*plVar12 + 0x18))(plVar12);
          }
        }
      }
      plVar1 = local_58;
      if (local_58 != (long *)0x0) {
        plVar12 = local_58 + 1;
        do {
          iVar6 = (int)*plVar12 + -1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
          if (bVar3) {
            *(int *)plVar12 = iVar6;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar6 == 0) {
          (**(code **)(*local_58 + 0x10))(local_58);
          piVar11 = (int *)((long)plVar1 + 0xc);
          do {
            iVar6 = *piVar11;
                    /* try { // try from 02b3c49c to 02c3c4cb has its CatchHandler @ 02b3db40 */
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
            if (bVar3) {
              *piVar11 = iVar6 + -1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 + -1 == 0) {
            (**(code **)(*plVar1 + 0x18))(plVar1);
          }
        }
      }
      plVar1 = local_e0;
      if (local_e0 != (long *)0x0) {
        plVar12 = local_e0 + 1;
        do {
          iVar6 = (int)*plVar12 + -1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
          if (bVar3) {
            *(int *)plVar12 = iVar6;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar6 == 0) {
          (**(code **)(*local_e0 + 0x10))(local_e0);
          piVar11 = (int *)((long)plVar1 + 0xc);
          do {
            iVar6 = *piVar11;
                    /* try { // try from 02b3c4f0 to 02c3c51f has its CatchHandler @ 02b3d8cc */
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
            if (bVar3) {
              *piVar11 = iVar6 + -1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 + -1 == 0) {
            (**(code **)(*plVar1 + 0x18))(plVar1);
          }
        }
      }
    }
    else {
      iVar6 = _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv(*(undefined8 *)(param_1 + 0x70));
      if (iVar6 == 1) {
        local_f8 = *param_2;
        local_f0 = (long *)param_2[1];
        if (local_f0 != (long *)0x0) {
                    /* try { // try from 02b3c290 to 02c3c2bf has its CatchHandler @ 02b3d4ec */
          plVar1 = local_f0 + 1;
          do {
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
            if (bVar3) {
              *(int *)plVar1 = (int)*plVar1 + 1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
        }
        _ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                  (&local_60,param_1,&local_f8);
        plVar1 = local_58;
        lVar7 = local_60;
        local_60 = 0;
        local_58 = (long *)0x0;
        plVar12 = (long *)param_2[1];
        *param_2 = lVar7;
        param_2[1] = (long)plVar1;
        if (plVar12 != (long *)0x0) {
          plVar1 = plVar12 + 1;
          do {
            iVar6 = (int)*plVar1 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
            if (bVar3) {
              *(int *)plVar1 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*plVar12 + 0x10))(plVar12);
            piVar11 = (int *)((long)plVar12 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar12 + 0x18))(plVar12);
            }
          }
        }
                    /* try { // try from 02b3c318 to 02c3c327 has its CatchHandler @ 02b3d678 */
        plVar1 = local_58;
        if (local_58 != (long *)0x0) {
          plVar12 = local_58 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
                    /* try { // try from 02b3c32c to 02c3c33b has its CatchHandler @ 02b3db40 */
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
                    /* try { // try from 02b3c340 to 02c3c34f has its CatchHandler @ 02b3da70 */
            (**(code **)(*local_58 + 0x10))(local_58);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
                    /* try { // try from 02b3c354 to 02c3c363 has its CatchHandler @ 02b3d8d0 */
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c368 to 02c3c377 has its CatchHandler @ 02b3d798 */
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
        plVar1 = local_f0;
        if (local_f0 != (long *)0x0) {
          plVar12 = local_f0 + 1;
          do {
            iVar6 = (int)*plVar12 + -1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
            if (bVar3) {
              *(int *)plVar12 = iVar6;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar6 == 0) {
            (**(code **)(*local_f0 + 0x10))(local_f0);
            piVar11 = (int *)((long)plVar1 + 0xc);
            do {
              iVar6 = *piVar11;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
              if (bVar3) {
                *piVar11 = iVar6 + -1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 + -1 == 0) {
              (**(code **)(*plVar1 + 0x18))(plVar1);
            }
          }
        }
      }
      else {
        iVar6 = _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv
                          (*(undefined8 *)(param_1 + 0x70));
        if (iVar6 == 2) {
          local_108 = *param_2;
          local_100 = (long *)param_2[1];
          if (local_100 != (long *)0x0) {
            plVar1 = local_100 + 1;
            do {
                    /* try { // try from 02b3c544 to 02c3c573 has its CatchHandler @ 02b3d8c8 */
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
              if (bVar3) {
                *(int *)plVar1 = (int)*plVar1 + 1;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
          }
          _ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                    (&local_60,param_1,&local_108);
          plVar1 = local_58;
          lVar7 = local_60;
          local_60 = 0;
          local_58 = (long *)0x0;
          plVar12 = (long *)param_2[1];
          *param_2 = lVar7;
          param_2[1] = (long)plVar1;
          if (plVar12 != (long *)0x0) {
            plVar1 = plVar12 + 1;
            do {
                    /* try { // try from 02b3c578 to 02c3c57f has its CatchHandler @ 02b3d9b0 */
              iVar6 = (int)*plVar1 + -1;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
              if (bVar3) {
                *(int *)plVar1 = iVar6;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 == 0) {
                    /* try { // try from 02b3c58c to 02c3c597 has its CatchHandler @ 02b3dc00 */
              (**(code **)(*plVar12 + 0x10))(plVar12);
              piVar11 = (int *)((long)plVar12 + 0xc);
              do {
                iVar6 = *piVar11;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                if (bVar3) {
                  *piVar11 = iVar6 + -1;
                  cVar2 = ExclusiveMonitorsStatus();
                }
                    /* try { // try from 02b3c5a8 to 02c3c5bb has its CatchHandler @ 02b3d8c4 */
              } while (cVar2 != '\0');
              if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c5bc to 02c3c5c7 has its CatchHandler @ 02b3d858 */
                (**(code **)(*plVar12 + 0x18))(plVar12);
              }
            }
          }
          plVar1 = local_58;
          if (local_58 != (long *)0x0) {
            plVar12 = local_58 + 1;
            do {
              iVar6 = (int)*plVar12 + -1;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
              if (bVar3) {
                *(int *)plVar12 = iVar6;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 == 0) {
                    /* try { // try from 02b3c5e0 to 02c3c5ff has its CatchHandler @ 02b3dc00 */
              (**(code **)(*local_58 + 0x10))(local_58);
              piVar11 = (int *)((long)plVar1 + 0xc);
              do {
                iVar6 = *piVar11;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                if (bVar3) {
                  *piVar11 = iVar6 + -1;
                  cVar2 = ExclusiveMonitorsStatus();
                }
                    /* try { // try from 02b3c600 to 02c3c60b has its CatchHandler @ 02b3d9ac */
              } while (cVar2 != '\0');
              if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c60c to 02c3c61f has its CatchHandler @ 02b3d994 */
                (**(code **)(*plVar1 + 0x18))(plVar1);
              }
            }
          }
          plVar1 = local_100;
          if (local_100 != (long *)0x0) {
                    /* try { // try from 02b3c620 to 02c3c62b has its CatchHandler @ 02b3d990 */
            plVar12 = local_100 + 1;
            do {
              iVar6 = (int)*plVar12 + -1;
              cVar2 = '\x01';
              bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
              if (bVar3) {
                *(int *)plVar12 = iVar6;
                cVar2 = ExclusiveMonitorsStatus();
              }
            } while (cVar2 != '\0');
            if (iVar6 == 0) {
              (**(code **)(*local_100 + 0x10))(local_100);
              piVar11 = (int *)((long)plVar1 + 0xc);
              do {
                iVar6 = *piVar11;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                if (bVar3) {
                  *piVar11 = iVar6 + -1;
                  cVar2 = ExclusiveMonitorsStatus();
                }
              } while (cVar2 != '\0');
              if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c660 to 02c3c68f has its CatchHandler @ 02b3d794 */
                (**(code **)(*plVar1 + 0x18))(plVar1);
              }
            }
          }
        }
        else {
          iVar6 = _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv
                            (*(undefined8 *)(param_1 + 0x70));
          if (iVar6 == 3) {
            local_118 = *param_2;
            local_110 = (long *)param_2[1];
            if (local_110 != (long *)0x0) {
              plVar1 = local_110 + 1;
              do {
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
                if (bVar3) {
                  *(int *)plVar1 = (int)*plVar1 + 1;
                  cVar2 = ExclusiveMonitorsStatus();
                }
              } while (cVar2 != '\0');
            }
                    /* try { // try from 02b3c6b8 to 02c3c6e7 has its CatchHandler @ 02b3d790 */
            _ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                      (&local_60,param_1,&local_118);
            plVar1 = local_58;
            lVar7 = local_60;
            local_60 = 0;
            local_58 = (long *)0x0;
            plVar12 = (long *)param_2[1];
            *param_2 = lVar7;
            param_2[1] = (long)plVar1;
            if (plVar12 != (long *)0x0) {
              plVar1 = plVar12 + 1;
              do {
                iVar6 = (int)*plVar1 + -1;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
                if (bVar3) {
                  *(int *)plVar1 = iVar6;
                  cVar2 = ExclusiveMonitorsStatus();
                }
              } while (cVar2 != '\0');
              if (iVar6 == 0) {
                (**(code **)(*plVar12 + 0x10))(plVar12);
                piVar11 = (int *)((long)plVar12 + 0xc);
                do {
                  iVar6 = *piVar11;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                  if (bVar3) {
                    *piVar11 = iVar6 + -1;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 + -1 == 0) {
                  (**(code **)(*plVar12 + 0x18))(plVar12);
                }
              }
            }
            plVar1 = local_58;
            if (local_58 != (long *)0x0) {
              plVar12 = local_58 + 1;
              do {
                    /* try { // try from 02b3c72c to 02c3c76b has its CatchHandler @ 02b3da70 */
                iVar6 = (int)*plVar12 + -1;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
                if (bVar3) {
                  *(int *)plVar12 = iVar6;
                  cVar2 = ExclusiveMonitorsStatus();
                }
              } while (cVar2 != '\0');
              if (iVar6 == 0) {
                (**(code **)(*local_58 + 0x10))(local_58);
                piVar11 = (int *)((long)plVar1 + 0xc);
                do {
                  iVar6 = *piVar11;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                  if (bVar3) {
                    *piVar11 = iVar6 + -1;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 + -1 == 0) {
                  (**(code **)(*plVar1 + 0x18))(plVar1);
                }
              }
            }
            plVar1 = local_110;
            if (local_110 != (long *)0x0) {
              plVar12 = local_110 + 1;
              do {
                iVar6 = (int)*plVar12 + -1;
                cVar2 = '\x01';
                bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
                if (bVar3) {
                  *(int *)plVar12 = iVar6;
                  cVar2 = ExclusiveMonitorsStatus();
                }
                    /* try { // try from 02b3c790 to 02c3c7bf has its CatchHandler @ 02b3d78c */
              } while (cVar2 != '\0');
              if (iVar6 == 0) {
                (**(code **)(*local_110 + 0x10))(local_110);
                piVar11 = (int *)((long)plVar1 + 0xc);
                do {
                  iVar6 = *piVar11;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                  if (bVar3) {
                    *piVar11 = iVar6 + -1;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 + -1 == 0) {
                  (**(code **)(*plVar1 + 0x18))(plVar1);
                }
              }
            }
          }
          else {
            iVar6 = _ZN5Sfs2X3FSM18FiniteStateMachine15GetCurrentStateEv
                              (*(undefined8 *)(param_1 + 0x70));
            if (iVar6 == 4) {
                    /* try { // try from 02b3c7e4 to 02c3c813 has its CatchHandler @ 02b3d788 */
              local_128 = *param_2;
              local_120 = (long *)param_2[1];
              if (local_120 != (long *)0x0) {
                plVar1 = local_120 + 1;
                do {
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
                  if (bVar3) {
                    *(int *)plVar1 = (int)*plVar1 + 1;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
              }
                    /* try { // try from 02b3c818 to 02c3c85f has its CatchHandler @ 02b3dc00 */
              _ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
                        (&local_60,param_1,&local_128);
              plVar1 = local_58;
              lVar7 = local_60;
              local_60 = 0;
              local_58 = (long *)0x0;
              plVar12 = (long *)param_2[1];
              *param_2 = lVar7;
              param_2[1] = (long)plVar1;
              if (plVar12 != (long *)0x0) {
                plVar1 = plVar12 + 1;
                do {
                  iVar6 = (int)*plVar1 + -1;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
                  if (bVar3) {
                    *(int *)plVar1 = iVar6;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 == 0) {
                  (**(code **)(*plVar12 + 0x10))(plVar12);
                  piVar11 = (int *)((long)plVar12 + 0xc);
                  do {
                    iVar6 = *piVar11;
                    /* try { // try from 02b3c860 to 02c3c873 has its CatchHandler @ 02b3d784 */
                    cVar2 = '\x01';
                    bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                    if (bVar3) {
                      *piVar11 = iVar6 + -1;
                      cVar2 = ExclusiveMonitorsStatus();
                    }
                  } while (cVar2 != '\0');
                  if (iVar6 + -1 == 0) {
                    /* try { // try from 02b3c874 to 02c3c87f has its CatchHandler @ 02b3d780 */
                    (**(code **)(*plVar12 + 0x18))(plVar12);
                  }
                }
              }
              plVar1 = local_58;
              if (local_58 != (long *)0x0) {
                plVar12 = local_58 + 1;
                do {
                  iVar6 = (int)*plVar12 + -1;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
                  if (bVar3) {
                    *(int *)plVar12 = iVar6;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 == 0) {
                  (**(code **)(*local_58 + 0x10))(local_58);
                  piVar11 = (int *)((long)plVar1 + 0xc);
                  do {
                    iVar6 = *piVar11;
                    cVar2 = '\x01';
                    bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                    if (bVar3) {
                      *piVar11 = iVar6 + -1;
                      cVar2 = ExclusiveMonitorsStatus();
                    }
                  } while (cVar2 != '\0');
                    /* try { // try from 02b3c8c4 to 02c3c8f3 has its CatchHandler @ 02b3d8d0 */
                  if (iVar6 + -1 == 0) {
                    (**(code **)(*plVar1 + 0x18))(plVar1);
                  }
                }
              }
              plVar1 = local_120;
              if (local_120 != (long *)0x0) {
                plVar12 = local_120 + 1;
                do {
                  iVar6 = (int)*plVar12 + -1;
                  cVar2 = '\x01';
                  bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
                  if (bVar3) {
                    *(int *)plVar12 = iVar6;
                    cVar2 = ExclusiveMonitorsStatus();
                  }
                } while (cVar2 != '\0');
                if (iVar6 == 0) {
                  (**(code **)(*local_120 + 0x10))(local_120);
                  piVar11 = (int *)((long)plVar1 + 0xc);
                  do {
                    iVar6 = *piVar11;
                    cVar2 = '\x01';
                    bVar3 = (bool)ExclusiveMonitorPass(piVar11,0x10);
                    if (bVar3) {
                      *piVar11 = iVar6 + -1;
                      cVar2 = ExclusiveMonitorsStatus();
                    }
                    /* try { // try from 02b3c918 to 02c3c947 has its CatchHandler @ 02b3d75c */
                  } while (cVar2 != '\0');
                  if (iVar6 + -1 == 0) {
                    (**(code **)(*plVar1 + 0x18))(plVar1);
                  }
                }
              }
            }
          }
        }
      }
    }
    lVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_2);
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b3d1bc
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler15HandleNewPacketEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  long *plVar6;
  int iVar7;
  undefined8 *puVar8;
  long *plVar9;
  undefined8 uVar10;
  long *plVar11;
  long lVar12;
  undefined8 local_f8;
  long *plStack_f0;
  undefined8 local_e8;
  long *local_e0;
  undefined8 local_d8;
  long *local_d0;
  undefined8 local_c8;
  long *local_c0;
  undefined1 local_b4 [4];
  long local_b0;
  long *local_a8;
  undefined8 *local_a0;
  long *local_98;
  long *local_90;
  long *local_88;
  long local_80;
  long *local_78;
  long *local_70;
  long local_68;
  
  lVar5 = tpidr_el0;
  local_68 = *(long *)(lVar5 + 0x28);
  puVar8 = (undefined8 *)_Znwm(0x18);
  puVar8[1] = 0;
  puVar8[2] = 0;
  *puVar8 = 0;
  _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_80,puVar8);
  plVar9 = (long *)_Znwm(8);
  *plVar9 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_90,plVar9);
  uVar10 = _Znwm(8);
  FUN_0307a6fc(uVar10,"Handling New Packet of size %d",&local_c8);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_a0,uVar10);
  plVar6 = local_88;
  plVar11 = local_90;
  plVar9 = local_98;
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  if (local_98 != (long *)0x0) {
    plVar1 = local_98 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b3d2a0 to 02c3d2af has its CatchHandler @ 02b3d2b4 */
  uVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
                    /* try { // try from 02b3d2b0 to 02c3d32f has its CatchHandler @ 02b3be5c */
  lVar12 = *(long *)(*plVar11 + -0x18);
                    /* catch() { ... } // from try @ 02b3d2a0 with catch @ 02b3d2b4 */
                    /* catch() { ... } // from try @ 02b3d1b0 with catch @ 02b3d2b8 */
                    /* catch() { ... } // from try @ 02b3d14c with catch @ 02b3d2bc */
                    /* catch() { ... } // from try @ 02b3d0f8 with catch @ 02b3d2c0 */
  FUN_0307d194(plVar11,lVar12 + 0x1000,0);
                    /* catch() { ... } // from try @ 02b3d01c with catch @ 02b3d2c4 */
                    /* catch() { ... } // from try @ 02b3cfc4 with catch @ 02b3d2c8 */
                    /* catch() { ... } // from try @ 02b3cf04 with catch @ 02b3d2cc */
                    /* catch() { ... } // from try @ 02b3ceb0 with catch @ 02b3d2d0 */
  iVar7 = sprintf((char *)*plVar11,(char *)*local_a0,uVar10);
                    /* catch() { ... } // from try @ 02b3cf84 with catch @ 02b3d2d4 */
  if (iVar7 < 0) {
                    /* catch() { ... } // from try @ 02b3d384 with catch @ 02b3d3b8 */
                    /* catch() { ... } // from try @ 02b3d330 with catch @ 02b3d3bc */
                    /* catch() { ... } // from try @ 02b3ce34 with catch @ 02b3d3c0
                       catch() { ... } // from try @ 02b3ce7c with catch @ 02b3d3c0 */
    FUN_0307d194(plVar11,lVar12,0);
  }
  else {
                    /* catch() { ... } // from try @ 02b3cf70 with catch @ 02b3d2d8 */
    FUN_0307d194(plVar11,lVar12 + iVar7,0);
  }
  if (plVar9 != (long *)0x0) {
    plVar11 = plVar9 + 1;
    do {
                    /* catch() { ... } // from try @ 02b3cf64 with catch @ 02b3d2f0 */
                    /* catch() { ... } // from try @ 02b3cde4 with catch @ 02b3d2f4 */
      iVar7 = (int)*plVar11 + -1;
                    /* catch() { ... } // from try @ 02b3cdd0 with catch @ 02b3d2f8 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
                    /* catch() { ... } // from try @ 02b3d090 with catch @ 02b3d308 */
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b3d330 to 02c3d35f has its CatchHandler @ 02b3d3bc */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  if (plVar6 != (long *)0x0) {
    plVar9 = plVar6 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b3d384 to 02c3d3b3 has its CatchHandler @ 02b3d3b8 */
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  lVar12 = local_80;
  if (*(long *)(local_80 + 8) == *(long *)(local_80 + 0x10)) {
    _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_80,local_90);
  }
  else {
    FUN_0307e06c();
    *(long *)(lVar12 + 8) = *(long *)(lVar12 + 8) + 8;
  }
  uVar10 = *(undefined8 *)(param_2 + 0x38);
  local_b0 = local_80;
  local_a8 = local_78;
  if (local_78 != (long *)0x0) {
    plVar9 = local_78 + 1;
    do {
                    /* try { // try from 02b3d3e8 to 02c3d417 has its CatchHandler @ 02b3d474 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar10,&local_b0);
  plVar9 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar11 = local_a8 + 1;
    do {
      iVar7 = (int)*plVar11 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* try { // try from 02b3d43c to 02c3d46b has its CatchHandler @ 02b3d470 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  _ZN5Sfs2X4Util9ByteArray8ReadByteERh(*param_3,local_b4);
  _ZN5Sfs2X4Core12PacketHeader10FromBinaryEl(&local_c8,local_b4[0]);
                    /* catch() { ... } // from try @ 02b3d43c with catch @ 02b3d470 */
                    /* catch() { ... } // from try @ 02b3d3e8 with catch @ 02b3d474 */
  uVar10 = _Znwm(0x20);
                    /* catch() { ... } // from try @ 02b3cdbc with catch @ 02b3d478 */
                    /* catch() { ... } // from try @ 02b3cf3c with catch @ 02b3d47c
                       catch() { ... } // from try @ 02b3d184 with catch @ 02b3d47c */
  local_e8 = local_c8;
  local_e0 = local_c0;
  if (local_c0 != (long *)0x0) {
    plVar9 = local_c0 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b3d4a8 to 02c3d4d7 has its CatchHandler @ 02b3d4dc */
  _ZN5Sfs2X8Bitswarm13PendingPacketC1EN5boost10shared_ptrINS_4Core12PacketHeaderEEE
            (uVar10,&local_e8);
  local_d0 = (long *)0x0;
  local_d8 = uVar10;
  _ZN5boost6detail12shared_countC2IN5Sfs2X8Bitswarm13PendingPacketEEEPT_(&local_70,uVar10);
  plVar9 = local_d0;
  local_d0 = local_70;
  local_70 = plVar9;
  if (plVar9 != (long *)0x0) {
    plVar11 = plVar9 + 1;
    do {
                    /* catch() { ... } // from try @ 02b3d4a8 with catch @ 02b3d4dc */
      iVar7 = (int)*plVar11 + -1;
                    /* catch() { ... } // from try @ 02b3c1e0 with catch @ 02b3d4e0 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* catch() { ... } // from try @ 02b3c17c with catch @ 02b3d4e4 */
    } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3c128 with catch @ 02b3d4e8 */
    if (iVar7 == 0) {
                    /* catch() { ... } // from try @ 02b3c290 with catch @ 02b3d4ec */
                    /* catch() { ... } // from try @ 02b3c238 with catch @ 02b3d4f0 */
                    /* catch() { ... } // from try @ 02b3c000 with catch @ 02b3d4f4 */
                    /* catch() { ... } // from try @ 02b3bfac with catch @ 02b3d4f8 */
      (**(code **)(*plVar9 + 0x10))(plVar9);
                    /* catch() { ... } // from try @ 02b3c1b4 with catch @ 02b3d4fc */
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b3c084 with catch @ 02b3d50c */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3c070 with catch @ 02b3d510 */
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3c0d4 with catch @ 02b3d528
                       catch() { ... } // from try @ 02b3ce68 with catch @ 02b3d528 */
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_d8,uVar10,uVar10);
  plVar9 = local_d0;
  uVar10 = local_d8;
  local_d8 = 0;
  local_d0 = (long *)0x0;
  plVar11 = *(long **)(param_2 + 0x50);
  *(undefined8 *)(param_2 + 0x48) = uVar10;
  *(long **)(param_2 + 0x50) = plVar9;
  if (plVar11 != (long *)0x0) {
    plVar9 = plVar11 + 1;
    do {
                    /* try { // try from 02b3d550 to 02c3d57f has its CatchHandler @ 02b3d634 */
      iVar7 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar2 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar9 = local_d0;
  if (local_d0 != (long *)0x0) {
    plVar11 = local_d0 + 1;
    do {
                    /* try { // try from 02b3d5a4 to 02c3d5d3 has its CatchHandler @ 02b3d630 */
      iVar7 = (int)*plVar11 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_d0 + 0x10))(local_d0);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_e0;
  if (local_e0 != (long *)0x0) {
    plVar11 = local_e0 + 1;
    do {
                    /* try { // try from 02b3d5fc to 02c3d62b has its CatchHandler @ 02b3d638 */
      iVar7 = (int)*plVar11 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_e0 + 0x10))(local_e0);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b3d5a4 with catch @ 02b3d630 */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3d550 with catch @ 02b3d634 */
      if (iVar7 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3d5fc with catch @ 02b3d638 */
                    /* catch() { ... } // from try @ 02b3bef8 with catch @ 02b3d63c */
                    /* catch() { ... } // from try @ 02b3bee4 with catch @ 02b3d640 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),0);
  local_f8 = *param_3;
  plVar9 = (long *)param_3[1];
                    /* catch() { ... } // from try @ 02b3bed8 with catch @ 02b3d658 */
  uVar10 = local_f8;
  if (plVar9 != (long *)0x0) {
    plVar11 = plVar9 + 1;
    do {
                    /* catch() { ... } // from try @ 02b3bebc with catch @ 02b3d668 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    uVar10 = *param_3;
  }
  plStack_f0 = plVar9;
                    /* catch() { ... } // from try @ 02b3bf40 with catch @ 02b3d678
                       catch() { ... } // from try @ 02b3c318 with catch @ 02b3d678 */
  uVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(uVar10);
  _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
            (param_1,uVar10,&local_f8,1);
  if (plVar9 != (long *)0x0) {
    plVar11 = plVar9 + 1;
    do {
      iVar7 = (int)*plVar11 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar4) {
        *(int *)plVar11 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3d6a0 to 02c3d6cf has its CatchHandler @ 02b3d72c */
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  if (local_c0 != (long *)0x0) {
    plVar9 = local_c0 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
                    /* try { // try from 02b3d6f4 to 02c3d723 has its CatchHandler @ 02b3d728 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_c0 + 0x10))(local_c0);
      piVar2 = (int *)((long)local_c0 + 0xc);
      do {
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3d6f4 with catch @ 02b3d728 */
                    /* catch() { ... } // from try @ 02b3d6a0 with catch @ 02b3d72c */
                    /* catch() { ... } // from try @ 02b3c038 with catch @ 02b3d730 */
        (**(code **)(*local_c0 + 0x18))(local_c0);
      }
    }
  }
  if (local_98 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b3cc4c with catch @ 02b3d740 */
    plVar9 = local_98 + 1;
    do {
                    /* catch() { ... } // from try @ 02b3cba0 with catch @ 02b3d744 */
                    /* catch() { ... } // from try @ 02b3cb4c with catch @ 02b3d748 */
      iVar7 = (int)*plVar9 + -1;
                    /* catch() { ... } // from try @ 02b3ca84 with catch @ 02b3d74c */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* catch() { ... } // from try @ 02b3ca2c with catch @ 02b3d750 */
    } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3cd8c with catch @ 02b3d754 */
    if (iVar7 == 0) {
                    /* catch() { ... } // from try @ 02b3c96c with catch @ 02b3d758 */
                    /* catch() { ... } // from try @ 02b3c918 with catch @ 02b3d75c */
                    /* catch() { ... } // from try @ 02b3c9ec with catch @ 02b3d760 */
                    /* catch() { ... } // from try @ 02b3cd18 with catch @ 02b3d764 */
      (**(code **)(*local_98 + 0x10))(local_98);
                    /* catch() { ... } // from try @ 02b3ccc0 with catch @ 02b3d768 */
      piVar2 = (int *)((long)local_98 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b3c9d8 with catch @ 02b3d76c */
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02b3c9cc with catch @ 02b3d77c */
      if (iVar7 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3c874 with catch @ 02b3d780 */
                    /* catch() { ... } // from try @ 02b3c860 with catch @ 02b3d784 */
                    /* catch() { ... } // from try @ 02b3c7e4 with catch @ 02b3d788 */
                    /* catch() { ... } // from try @ 02b3c790 with catch @ 02b3d78c */
        (**(code **)(*local_98 + 0x18))(local_98);
      }
    }
  }
                    /* catch() { ... } // from try @ 02b3c6b8 with catch @ 02b3d790 */
                    /* catch() { ... } // from try @ 02b3c660 with catch @ 02b3d794 */
  if (local_88 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b3c368 with catch @ 02b3d798
                       catch() { ... } // from try @ 02b3caf8 with catch @ 02b3d798 */
    plVar9 = local_88 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar2 = (int *)((long)local_88 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* try { // try from 02b3d7c8 to 02c3d7f7 has its CatchHandler @ 02b3d854 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_88 + 0x18))(local_88);
      }
    }
  }
  if (local_78 != (long *)0x0) {
    plVar9 = local_78 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar7;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar2 = (int *)((long)local_78 + 0xc);
      do {
                    /* try { // try from 02b3d81c to 02c3d84b has its CatchHandler @ 02b3d850 */
        iVar7 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar7 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_78 + 0x18))(local_78);
      }
    }
  }
  if (*(long *)(lVar5 + 0x28) == local_68) {
                    /* catch() { ... } // from try @ 02b3d81c with catch @ 02b3d850 */
                    /* catch() { ... } // from try @ 02b3d7c8 with catch @ 02b3d854 */
                    /* catch() { ... } // from try @ 02b3c5bc with catch @ 02b3d858 */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b3dd00
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler14HandleDataSizeEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 *param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  char *pcVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  long lVar6;
  undefined *puVar7;
  undefined *puVar8;
  int iVar9;
  undefined8 *puVar10;
  long *plVar11;
  undefined8 uVar12;
  ulong uVar13;
  undefined *__ptr;
  undefined8 uVar14;
  int *piVar15;
  long *plVar16;
  long lVar17;
  long lVar18;
  undefined1 auStack_138 [8];
  long *local_130;
  undefined8 local_128;
  long *local_120;
  undefined8 local_118;
  long *local_110;
  undefined8 local_108;
  long *local_100;
  long *local_f8;
  long *local_f0;
  undefined1 auStack_e8 [8];
  undefined8 *local_e0;
  long *local_d8;
  undefined8 local_d0;
  long *local_c8;
  uint local_bc;
  long *local_b8;
  long *local_b0;
  undefined8 local_a8;
  long *local_a0;
  undefined8 *local_98;
  long *local_90;
  long *local_88;
  long *local_80;
  long *local_78;
  long *local_70;
  long local_68;
  
                    /* try { // try from 02b3dd14 to 02c3dd43 has its CatchHandler @ 02b3dee0 */
  lVar6 = tpidr_el0;
  local_68 = *(long *)(lVar6 + 0x28);
  puVar10 = (undefined8 *)_Znwm(0x18);
  puVar10[1] = 0;
  puVar10[2] = 0;
  *puVar10 = 0;
  _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_78,puVar10);
  plVar11 = (long *)_Znwm(8);
  puVar7 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02b3dd6c to 02c3dd9b has its CatchHandler @ 02b3dee4 */
  *plVar11 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_88,plVar11);
  uVar12 = _Znwm(8);
  FUN_0307a6fc(uVar12,"Handling Header Size. Length: %d (%s)",&local_e0);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_98,uVar12);
  plVar3 = local_80;
  plVar16 = local_88;
  plVar11 = local_90;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
                    /* try { // try from 02b3ddc4 to 02c3ddf3 has its CatchHandler @ 02b3dee8 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  uVar12 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
                    /* try { // try from 02b3ddf4 to 02c3deeb has its CatchHandler @ 02b3be5c */
  _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_a8,*(undefined8 *)(param_2 + 0x48));
  uVar13 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(local_a8);
  lVar17 = *(long *)(*plVar16 + -0x18);
  FUN_0307d194(plVar16,lVar17 + 0x1000,0);
  pcVar2 = "big";
  if ((uVar13 & 1) == 0) {
    pcVar2 = "small";
  }
  iVar9 = sprintf((char *)*plVar16,(char *)*local_98,uVar12,pcVar2);
  if (iVar9 < 0) {
    FUN_0307d194(plVar16,lVar17,0);
  }
  else {
    FUN_0307d194(plVar16,lVar17 + iVar9,0);
  }
  if (local_a0 != (long *)0x0) {
    plVar16 = local_a0 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_a0 + 0x10))(local_a0);
      piVar15 = (int *)((long)local_a0 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_a0 + 0x18))(local_a0);
      }
    }
  }
  if (plVar11 != (long *)0x0) {
    plVar16 = plVar11 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
                    /* catch() { ... } // from try @ 02b3dc44 with catch @ 02b3ded8 */
                    /* catch() { ... } // from try @ 02b3dc9c with catch @ 02b3dedc */
                    /* catch() { ... } // from try @ 02b3dd14 with catch @ 02b3dee0 */
      (**(code **)(*plVar11 + 0x10))(plVar11);
                    /* catch() { ... } // from try @ 02b3dd6c with catch @ 02b3dee4 */
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b3ddc4 with catch @ 02b3dee8 */
        iVar9 = *piVar15;
                    /* catch() { ... } // from try @ 02b3df84 with catch @ 02b3deec
                       catch() { ... } // from try @ 02b3dfc8 with catch @ 02b3deec */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b3df08 to 02c3df0f has its CatchHandler @ 02b3dfa4 */
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (plVar3 != (long *)0x0) {
    plVar11 = plVar3 + 1;
    do {
      iVar9 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar3 + 0x10))(plVar3);
      piVar15 = (int *)((long)plVar3 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b3df54 to 02c3df83 has its CatchHandler @ 02b3dfa0 */
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  plVar11 = local_78;
  if (local_78[1] == local_78[2]) {
                    /* catch() { ... } // from try @ 02b3df54 with catch @ 02b3dfa0 */
    _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_78,local_88);
  }
  else {
    FUN_0307e06c();
    plVar11[1] = plVar11[1] + 8;
                    /* try { // try from 02b3df84 to 02c3dfbb has its CatchHandler @ 02b3deec */
  }
                    /* catch() { ... } // from try @ 02b3df08 with catch @ 02b3dfa4 */
  uVar12 = *(undefined8 *)(param_2 + 0x38);
  local_b8 = local_78;
  local_b0 = local_70;
  if (local_70 != (long *)0x0) {
    plVar11 = local_70 + 1;
    do {
                    /* try { // try from 02b3dfbc to 02c3dfbf has its CatchHandler @ 02b3dfc0 */
                    /* catch() { ... } // from try @ 02b3dfbc with catch @ 02b3dfc0 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3dfc4 to 02c3dfc7 has its CatchHandler @ 02b3dfd0 */
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b3dfc8 to 02c3dfd3 has its CatchHandler @ 02b3deec */
  _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar12,&local_b8);
  plVar11 = local_b0;
                    /* catch() { ... } // from try @ 02b3dfc4 with catch @ 02b3dfd0 */
  if (local_b0 != (long *)0x0) {
    plVar16 = local_b0 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  local_bc = 0xffffffff;
  _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_d0,*(undefined8 *)(param_2 + 0x48));
                    /* try { // try from 02b3e03c to 02c3e06b has its CatchHandler @ 02b3e078 */
  uVar13 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(local_d0);
  if (local_c8 != (long *)0x0) {
    plVar11 = local_c8 + 1;
    do {
      iVar9 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3e03c with catch @ 02b3e078
                        */
      piVar15 = (int *)((long)local_c8 + 0xc);
      do {
                    /* try { // try from 02b3e07c to 02c3e0d7 has its CatchHandler @ 02b3e07c
                       catch() { ... } // from try @ 02b3e07c with catch @ 02b3e07c
                       catch() { ... } // from try @ 02b3e1a0 with catch @ 02b3e07c
                       catch() { ... } // from try @ 02b3e250 with catch @ 02b3e07c */
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_c8 + 0x18))(local_c8);
      }
    }
  }
  if ((uVar13 & 1) == 0) {
    lVar17 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    if (1 < lVar17) {
                    /* try { // try from 02b3e0d8 to 02c3e0e3 has its CatchHandler @ 02b3e1f4 */
      _ZN5Sfs2X4Util9ByteArray10ReadUShortERt(*param_3,&local_e0);
      local_bc = (uint)(ushort)local_e0;
    }
    uVar12 = 2;
  }
  else {
    lVar17 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    if (3 < lVar17) {
      _ZN5Sfs2X4Util9ByteArray7ReadIntERi(*param_3,&local_bc);
    }
    uVar12 = 4;
  }
  plVar1 = local_78;
  puVar8 = PTR_pthread_create_03bd6b78;
  plVar3 = (long *)local_78[1];
  plVar16 = (long *)*local_78;
  for (plVar11 = plVar16; plVar3 != plVar11; plVar11 = plVar11 + 1) {
    __ptr = (undefined *)(*plVar11 + -0x18);
    if (__ptr != puVar7) {
      piVar15 = (int *)(*plVar11 + -8);
      if (puVar8 == (undefined *)0x0) {
        iVar9 = *piVar15;
        *piVar15 = iVar9 + -1;
      }
      else {
        do {
          iVar9 = *piVar15;
                    /* try { // try from 02b3e118 to 02c3e147 has its CatchHandler @ 02b3e1f0 */
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
      }
      if (iVar9 < 1) {
        _ZdlPv(__ptr);
      }
    }
  }
  plVar1[1] = (long)plVar16;
                    /* try { // try from 02b3e170 to 02c3e19f has its CatchHandler @ 02b3e1ec */
  FUN_0307c7fc(local_88,0,*(undefined8 *)(*local_88 + -0x18),0);
  uVar14 = _Znwm(8);
  FUN_0307a6fc(uVar14,"Data size is %d",auStack_e8);
                    /* try { // try from 02b3e1a0 to 02c3e21f has its CatchHandler @ 02b3e07c */
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_e0,uVar14);
  plVar11 = local_90;
  local_90 = local_d8;
  local_98 = local_e0;
  local_e0 = (undefined8 *)0x0;
  local_d8 = (long *)0x0;
  if (plVar11 != (long *)0x0) {
    plVar16 = plVar11 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b3e170 with catch @ 02b3e1ec */
        iVar9 = *piVar15;
                    /* catch() { ... } // from try @ 02b3e118 with catch @ 02b3e1f0 */
                    /* catch() { ... } // from try @ 02b3e0d8 with catch @ 02b3e1f4 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_d8;
  if (local_d8 != (long *)0x0) {
    plVar16 = local_d8 + 1;
    do {
                    /* try { // try from 02b3e220 to 02c3e24f has its CatchHandler @ 02b3e258 */
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3e250 to 02c3e25b has its CatchHandler @ 02b3e07c */
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3e220 with catch @ 02b3e258 */
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar3 = local_80;
  plVar16 = local_88;
  plVar11 = local_90;
  puVar10 = local_98;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
                    /* try { // try from 02b3e278 to 02c3e2b3 has its CatchHandler @ 02b3e278
                       catch() { ... } // from try @ 02b3e278 with catch @ 02b3e278
                       catch() { ... } // from try @ 02b3e2b8 with catch @ 02b3e278
                       catch() { ... } // from try @ 02b3e460 with catch @ 02b3e278
                       catch() { ... } // from try @ 02b3e54c with catch @ 02b3e278
                       catch() { ... } // from try @ 02b3e5cc with catch @ 02b3e278 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  lVar18 = (long)(int)local_bc;
  lVar17 = *(long *)(*local_88 + -0x18);
                    /* try { // try from 02b3e2b4 to 02c3e2b7 has its CatchHandler @ 02b3e558 */
                    /* try { // try from 02b3e2b8 to 02c3e2cb has its CatchHandler @ 02b3e278 */
  FUN_0307d194(local_88,lVar17 + 0x1000,0);
  iVar9 = sprintf((char *)*plVar16,(char *)*puVar10,lVar18);
                    /* try { // try from 02b3e2cc to 02c3e2f3 has its CatchHandler @ 02b3e56c */
  if (iVar9 < 0) {
    FUN_0307d194(plVar16,lVar17,0);
  }
  else {
    FUN_0307d194(plVar16,lVar17 + iVar9,0);
  }
  if (plVar11 != (long *)0x0) {
    plVar16 = plVar11 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (plVar3 != (long *)0x0) {
    plVar11 = plVar3 + 1;
    do {
      iVar9 = (int)*plVar11 + -1;
                    /* try { // try from 02b3e344 to 02c3e357 has its CatchHandler @ 02b3e498 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar3 + 0x10))(plVar3);
      piVar15 = (int *)((long)plVar3 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b3e380 to 02c3e3af has its CatchHandler @ 02b3e494 */
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  plVar11 = local_78;
  if (local_78[1] == local_78[2]) {
    _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_78,local_88);
  }
  else {
    FUN_0307e06c();
    plVar11[1] = plVar11[1] + 8;
  }
  uVar14 = *(undefined8 *)(param_2 + 0x38);
  local_f8 = local_78;
  local_f0 = local_70;
                    /* try { // try from 02b3e3d8 to 02c3e407 has its CatchHandler @ 02b3e490 */
  if (local_70 != (long *)0x0) {
    plVar11 = local_70 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar14,&local_f8);
  plVar11 = local_f0;
  if (local_f0 != (long *)0x0) {
    plVar16 = local_f0 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_f0 + 0x10))(local_f0);
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
        iVar9 = *piVar15;
                    /* try { // try from 02b3e430 to 02c3e45f has its CatchHandler @ 02b3e48c */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (local_bc == 0xffffffff) {
    _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),2);
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_128,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_138,*param_3);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE
              (local_128,auStack_138);
    if (local_130 != (long *)0x0) {
      plVar11 = local_130 + 1;
      do {
        iVar9 = (int)*plVar11 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar5) {
          *(int *)plVar11 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_130 + 0x10))(local_130);
        piVar15 = (int *)((long)local_130 + 0xc);
        do {
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_130 + 0x18))(local_130);
        }
      }
    }
    if (local_120 != (long *)0x0) {
      plVar11 = local_120 + 1;
      do {
        iVar9 = (int)*plVar11 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar5) {
          *(int *)plVar11 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_120 + 0x10))(local_120);
        piVar15 = (int *)((long)local_120 + 0xc);
        do {
                    /* try { // try from 02b3e838 to 02c3e867 has its CatchHandler @ 02b3ee54 */
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_120 + 0x18))(local_120);
        }
      }
    }
    uVar12 = *(undefined8 *)(param_2 + 0x18);
    lVar17 = *(long *)(param_2 + 0x20);
    if (lVar17 != 0) {
      piVar15 = (int *)(lVar17 + 8);
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = *piVar15 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    plVar11 = (long *)param_3[1];
    *param_3 = uVar12;
    param_3[1] = lVar17;
    if (plVar11 != (long *)0x0) {
      plVar16 = plVar11 + 1;
      do {
        iVar9 = (int)*plVar16 + -1;
                    /* try { // try from 02b3e890 to 02c3e8bf has its CatchHandler @ 02b3ee50 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar5) {
          *(int *)plVar16 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar15 = (int *)((long)plVar11 + 0xc);
        do {
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
  }
  else {
                    /* try { // try from 02b3e460 to 02c3e4c3 has its CatchHandler @ 02b3e278 */
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_108,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl(local_108,(long)(int)local_bc);
    if (local_100 != (long *)0x0) {
      plVar11 = local_100 + 1;
      do {
        iVar9 = (int)*plVar11 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar5) {
          *(int *)plVar11 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02b3e430 with catch @ 02b3e48c */
      } while (cVar4 != '\0');
                    /* catch() { ... } // from try @ 02b3e3d8 with catch @ 02b3e490 */
      if (iVar9 == 0) {
                    /* catch() { ... } // from try @ 02b3e380 with catch @ 02b3e494 */
                    /* catch() { ... } // from try @ 02b3e344 with catch @ 02b3e498 */
        (**(code **)(*local_100 + 0x10))(local_100);
        piVar15 = (int *)((long)local_100 + 0xc);
        do {
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
                    /* try { // try from 02b3e4c4 to 02c3e4f3 has its CatchHandler @ 02b3e554 */
          (**(code **)(*local_100 + 0x18))(local_100);
        }
      }
    }
    local_118 = *param_3;
    local_110 = (long *)param_3[1];
    uVar14 = local_118;
    if (local_110 != (long *)0x0) {
      plVar11 = local_110 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar5) {
          *(int *)plVar11 = (int)*plVar11 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      uVar14 = *param_3;
    }
    uVar14 = _ZN5Sfs2X4Util9ByteArray6LengthEv(uVar14);
    _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
              (&local_e0,uVar14,&local_118,uVar12);
    plVar11 = local_d8;
    puVar10 = local_e0;
    local_e0 = (undefined8 *)0x0;
    local_d8 = (long *)0x0;
    plVar16 = (long *)param_3[1];
    *param_3 = puVar10;
    param_3[1] = plVar11;
    if (plVar16 != (long *)0x0) {
      plVar11 = plVar16 + 1;
      do {
                    /* try { // try from 02b3e51c to 02c3e54b has its CatchHandler @ 02b3e550 */
        iVar9 = (int)*plVar11 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar5) {
          *(int *)plVar11 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*plVar16 + 0x10))(plVar16);
        piVar15 = (int *)((long)plVar16 + 0xc);
        do {
          iVar9 = *piVar15;
                    /* try { // try from 02b3e54c to 02c3e59b has its CatchHandler @ 02b3e278 */
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
                    /* catch() { ... } // from try @ 02b3e51c with catch @ 02b3e550 */
        } while (cVar4 != '\0');
                    /* catch() { ... } // from try @ 02b3e4c4 with catch @ 02b3e554 */
        if (iVar9 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b3e2b4 with catch @ 02b3e558 */
          (**(code **)(*plVar16 + 0x18))(plVar16);
        }
      }
    }
    plVar11 = local_d8;
                    /* catch() { ... } // from try @ 02b3e2cc with catch @ 02b3e56c */
    if (local_d8 != (long *)0x0) {
      plVar16 = local_d8 + 1;
      do {
        iVar9 = (int)*plVar16 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar5) {
          *(int *)plVar16 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_d8 + 0x10))(local_d8);
        piVar15 = (int *)((long)plVar11 + 0xc);
        do {
                    /* try { // try from 02b3e59c to 02c3e5cb has its CatchHandler @ 02b3e5d4 */
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    plVar11 = local_110;
    if (local_110 != (long *)0x0) {
      plVar16 = local_110 + 1;
      do {
                    /* try { // try from 02b3e5cc to 02c3e5d7 has its CatchHandler @ 02b3e278 */
        iVar9 = (int)*plVar16 + -1;
                    /* catch() { ... } // from try @ 02b3e59c with catch @ 02b3e5d4 */
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar5) {
          *(int *)plVar16 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3e670 with catch @ 02b3e5d8
                       catch(type#1 @ 00000000) { ... } // from try @ 02b3e708 with catch @ 02b3e5d8
                        */
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_110 + 0x10))(local_110);
        piVar15 = (int *)((long)plVar11 + 0xc);
        do {
          iVar9 = *piVar15;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar5) {
            *piVar15 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
                    /* try { // try from 02b3e604 to 02c3e60b has its CatchHandler @ 02b3e6ac */
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),1);
  }
  plVar11 = local_90;
  *param_1 = *param_3;
  uVar12 = param_3[1];
  *param_3 = 0;
  param_3[1] = 0;
                    /* try { // try from 02b3e640 to 02c3e66f has its CatchHandler @ 02b3e6a8 */
  param_1[1] = uVar12;
  if (local_90 != (long *)0x0) {
    plVar16 = local_90 + 1;
    do {
      iVar9 = (int)*plVar16 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar5) {
        *(int *)plVar16 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
                    /* try { // try from 02b3e670 to 02c3e6d7 has its CatchHandler @ 02b3e5d8 */
      piVar15 = (int *)((long)plVar11 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (local_80 != (long *)0x0) {
    plVar11 = local_80 + 1;
    do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3e640 with catch @ 02b3e6a8
                        */
      iVar9 = (int)*plVar11 + -1;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3e604 with catch @ 02b3e6ac
                        */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar15 = (int *)((long)local_80 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3e6d8 to 02c3e707 has its CatchHandler @ 02b3e710 */
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
  if (local_70 != (long *)0x0) {
    plVar11 = local_70 + 1;
    do {
      iVar9 = (int)*plVar11 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar5) {
        *(int *)plVar11 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3e708 to 02c3e713 has its CatchHandler @ 02b3e5d8 */
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3e6d8 with catch @ 02b3e710
                        */
                    /* try { // try from 02b3e714 to 02c3e837 has its CatchHandler @ 02b3e714
                       catch() { ... } // from try @ 02b3e714 with catch @ 02b3e714
                       catch() { ... } // from try @ 02b3ee30 with catch @ 02b3e714
                       catch() { ... } // from try @ 02b3f1a4 with catch @ 02b3e714 */
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar15 = (int *)((long)local_70 + 0xc);
      do {
        iVar9 = *piVar15;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar5) {
          *piVar15 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_68) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b3ef40
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler22HandleDataSizeFragmentEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 *param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined *puVar6;
  undefined *puVar7;
  int iVar8;
  undefined8 *puVar9;
  long *plVar10;
  undefined8 uVar11;
  ulong uVar12;
  long lVar13;
  undefined8 uVar14;
  undefined *__ptr;
  int *piVar15;
  long *plVar16;
  long lVar17;
  long lVar18;
  undefined1 auStack_1f0 [8];
  long *local_1e8;
  undefined8 local_1e0;
  long *local_1d8;
  undefined8 local_1d0;
  long *local_1c8;
  undefined8 local_1c0;
  long *local_1b8;
  undefined8 local_1b0;
  long *local_1a8;
  undefined8 local_1a0;
  long *local_198;
  undefined8 local_190;
  long *local_188;
  long *local_180;
  long *local_178;
  undefined8 *local_170;
  long *local_168;
  short local_160;
  undefined6 uStack_15e;
  long *local_158;
  undefined8 local_150;
  long *local_148;
  int local_13c;
  undefined8 local_138;
  long *local_130;
  undefined1 auStack_128 [8];
  long *local_120;
  undefined8 local_118;
  long *local_110;
  undefined8 local_108;
  long *local_100;
  undefined1 auStack_f8 [8];
  long *local_f0;
  undefined8 local_e8;
  long *local_e0;
  undefined8 local_d8;
  long *local_d0;
  undefined8 local_c8;
  long *local_c0;
  undefined8 local_b8;
  long *local_b0;
  long *local_a8;
  long *local_a0;
  undefined8 *local_98;
  long *local_90;
  long *local_88;
  long *local_80;
  long *local_78;
  long *local_70;
  long local_68;
  
  lVar5 = tpidr_el0;
                    /* try { // try from 02b3ef68 to 02c3ef97 has its CatchHandler @ 02b3ef9c */
  local_68 = *(long *)(lVar5 + 0x28);
  puVar9 = (undefined8 *)_Znwm(0x18);
  puVar9[1] = 0;
  puVar9[2] = 0;
  *puVar9 = 0;
  _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_78,puVar9);
                    /* catch() { ... } // from try @ 02b3ef68 with catch @ 02b3ef9c */
                    /* catch() { ... } // from try @ 02b3ef10 with catch @ 02b3efa0 */
  plVar10 = (long *)_Znwm(8);
  puVar6 = PTR_DAT_03c37adf_1_03bd0478;
                    /* catch() { ... } // from try @ 02b3e970 with catch @ 02b3efa4 */
  *plVar10 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_88,plVar10);
  uVar11 = _Znwm(8);
  FUN_0307a6fc(uVar11,"Handling Size fragment. Data: %d",&local_118);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_98,uVar11);
  plVar2 = local_80;
  plVar16 = local_88;
  plVar10 = local_90;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* catch() { ... } // from try @ 02b3e968 with catch @ 02b3f010 */
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
                    /* catch() { ... } // from try @ 02b3e940 with catch @ 02b3f020 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  uVar11 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
                    /* catch() { ... } // from try @ 02b3ec3c with catch @ 02b3f034 */
  lVar17 = *(long *)(*plVar16 + -0x18);
  FUN_0307d194(plVar16,lVar17 + 0x1000,0);
  iVar8 = sprintf((char *)*plVar16,(char *)*local_98,uVar11);
  if (iVar8 < 0) {
    FUN_0307d194(plVar16,lVar17,0);
  }
  else {
                    /* try { // try from 02b3f060 to 02c3f08f has its CatchHandler @ 02b3f0ec */
    FUN_0307d194(plVar16,lVar17 + iVar8,0);
  }
  if (plVar10 != (long *)0x0) {
    plVar16 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar16 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar4) {
        *(int *)plVar16 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar15 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02b3f0b8 to 02c3f0e7 has its CatchHandler @ 02b3f0f0 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  if (plVar2 != (long *)0x0) {
    plVar10 = plVar2 + 1;
    do {
      iVar8 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
                    /* catch() { ... } // from try @ 02b3f060 with catch @ 02b3f0ec */
      (**(code **)(*plVar2 + 0x10))(plVar2);
                    /* catch() { ... } // from try @ 02b3f0b8 with catch @ 02b3f0f0 */
      piVar15 = (int *)((long)plVar2 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b3e934 with catch @ 02b3f0f4
                       catch() { ... } // from try @ 02b3e94c with catch @ 02b3f0f4 */
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar2 + 0x18))(plVar2);
      }
    }
  }
  plVar10 = local_78;
                    /* try { // try from 02b3f11c to 02c3f14b has its CatchHandler @ 02b3f1ac */
  if (local_78[1] == local_78[2]) {
    _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_78,local_88);
  }
  else {
    FUN_0307e06c();
    plVar10[1] = plVar10[1] + 8;
  }
  uVar11 = *(undefined8 *)(param_2 + 0x38);
  local_a8 = local_78;
  local_a0 = local_70;
  if (local_70 != (long *)0x0) {
    plVar10 = local_70 + 1;
    do {
                    /* try { // try from 02b3f174 to 02c3f1a3 has its CatchHandler @ 02b3f1b0 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = (int)*plVar10 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar11,&local_a8);
  plVar10 = local_a0;
  if (local_a0 != (long *)0x0) {
    plVar16 = local_a0 + 1;
    do {
      iVar8 = (int)*plVar16 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
      if (bVar4) {
        *(int *)plVar16 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
                    /* try { // try from 02b3f1a4 to 02c3f1b3 has its CatchHandler @ 02b3e714 */
    if (iVar8 == 0) {
                    /* catch() { ... } // from try @ 02b3f11c with catch @ 02b3f1ac */
                    /* catch() { ... } // from try @ 02b3f174 with catch @ 02b3f1b0 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3f268 with catch @ 02b3f1b4
                       catch(type#1 @ 00000000) { ... } // from try @ 02b3f2fc with catch @ 02b3f1b4
                        */
      (**(code **)(*local_a0 + 0x10))(local_a0);
      piVar15 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_b8,*(undefined8 *)(param_2 + 0x48));
  uVar12 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(local_b8);
  if ((uVar12 & 1) == 0) {
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_d8,*(undefined8 *)(param_2 + 0x48));
    lVar17 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_d8);
    lVar17 = 2 - lVar17;
    if (local_d0 != (long *)0x0) {
      plVar10 = local_d0 + 1;
      do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3f238 with catch @ 02b3f29c
                        */
        iVar8 = (int)*plVar10 + -1;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3f208 with catch @ 02b3f2a0
                        */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_d0 + 0x10))(local_d0);
        piVar15 = (int *)((long)local_d0 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b3f2cc to 02c3f2fb has its CatchHandler @ 02b3f304 */
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_d0 + 0x18))(local_d0);
        }
      }
    }
  }
  else {
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_c8,*(undefined8 *)(param_2 + 0x48));
                    /* try { // try from 02b3f208 to 02c3f20f has its CatchHandler @ 02b3f2a0 */
    lVar17 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_c8);
    lVar17 = 4 - lVar17;
    if (local_c0 != (long *)0x0) {
      plVar10 = local_c0 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b3f238 to 02c3f267 has its CatchHandler @ 02b3f29c */
        (**(code **)(*local_c0 + 0x10))(local_c0);
        piVar15 = (int *)((long)local_c0 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
                    /* try { // try from 02b3f268 to 02c3f2cb has its CatchHandler @ 02b3f1b4 */
          (**(code **)(*local_c0 + 0x18))(local_c0);
        }
      }
    }
  }
  if (local_b0 != (long *)0x0) {
    plVar10 = local_b0 + 1;
    do {
      iVar8 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b3f2fc to 02c3f307 has its CatchHandler @ 02b3f1b4 */
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b3f2cc with catch @ 02b3f304
                        */
                    /* catch() { ... } // from try @ 02b40e04 with catch @ 02b3f308
                       catch() { ... } // from try @ 02b41020 with catch @ 02b3f308
                       catch() { ... } // from try @ 02b41c28 with catch @ 02b3f308
                       catch() { ... } // from try @ 02b430d4 with catch @ 02b3f308 */
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar15 = (int *)((long)local_b0 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_b0 + 0x18))(local_b0);
      }
    }
  }
  lVar13 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
  if (lVar13 < lVar17) {
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_1e0,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_1f0,*param_3);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE
              (local_1e0,auStack_1f0);
                    /* try { // try from 02b3f37c to 02c3f387 has its CatchHandler @ 02b42f0c */
    if (local_1e8 != (long *)0x0) {
      plVar10 = local_1e8 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1e8 + 0x10))(local_1e8);
        piVar15 = (int *)((long)local_1e8 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3f3bc to 02c3f3eb has its CatchHandler @ 02b41d8c */
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_1e8 + 0x18))(local_1e8);
        }
      }
    }
    if (local_1d8 != (long *)0x0) {
      plVar10 = local_1d8 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1d8 + 0x10))(local_1d8);
        piVar15 = (int *)((long)local_1d8 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02b3f414 to 02c3f443 has its CatchHandler @ 02b41d44 */
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_1d8 + 0x18))(local_1d8);
        }
      }
    }
    uVar11 = *(undefined8 *)(param_2 + 0x18);
    lVar17 = *(long *)(param_2 + 0x20);
    if (lVar17 != 0) {
      piVar15 = (int *)(lVar17 + 8);
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = *piVar15 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plVar10 = (long *)param_3[1];
    *param_3 = uVar11;
    param_3[1] = lVar17;
    if (plVar10 != (long *)0x0) {
      plVar16 = plVar10 + 1;
      do {
        iVar8 = (int)*plVar16 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar4) {
          *(int *)plVar16 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b3f46c to 02c3f49b has its CatchHandler @ 02b41cfc */
        (**(code **)(*plVar10 + 0x10))(plVar10);
        piVar15 = (int *)((long)plVar10 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
  }
  else {
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_e8,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_f8,*param_3);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEEll
              (local_e8,auStack_f8,0,lVar17);
    if (local_f0 != (long *)0x0) {
      plVar10 = local_f0 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3f4e8 to 02c3f4f7 has its CatchHandler @ 02b42e50 */
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_f0 + 0x10))(local_f0);
        piVar15 = (int *)((long)local_f0 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_f0 + 0x18))(local_f0);
        }
      }
    }
                    /* try { // try from 02b3f52c to 02c3f55b has its CatchHandler @ 02b41d88 */
    if (local_e0 != (long *)0x0) {
      plVar10 = local_e0 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_e0 + 0x10))(local_e0);
        piVar15 = (int *)((long)local_e0 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_e0 + 0x18))(local_e0);
        }
      }
    }
                    /* try { // try from 02b3f584 to 02c3f5b3 has its CatchHandler @ 02b41d40 */
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_108,*(undefined8 *)(param_2 + 0x48));
    uVar12 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(local_108);
    uVar11 = 4;
    if ((uVar12 & 1) == 0) {
      uVar11 = 2;
    }
    if (local_100 != (long *)0x0) {
      plVar10 = local_100 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_100 + 0x10))(local_100);
        piVar15 = (int *)((long)local_100 + 0xc);
        do {
          iVar8 = *piVar15;
                    /* try { // try from 02b3f5dc to 02c3f60b has its CatchHandler @ 02b41cf8 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_100 + 0x18))(local_100);
        }
      }
    }
    uVar14 = _Znwm(0x890);
    _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar14);
    _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_118,uVar14);
    uVar14 = local_118;
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_138,*(undefined8 *)(param_2 + 0x48));
                    /* try { // try from 02b3f634 to 02c3f663 has its CatchHandler @ 02b41ca8 */
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_128,local_138);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEEll
              (uVar14,auStack_128,0,uVar11);
    if (local_120 != (long *)0x0) {
      plVar10 = local_120 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_120 + 0x10))(local_120);
        piVar15 = (int *)((long)local_120 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_120 + 0x18))(local_120);
        }
      }
    }
    if (local_130 != (long *)0x0) {
      plVar10 = local_130 + 1;
      do {
                    /* try { // try from 02b3f6b0 to 02c3f6bf has its CatchHandler @ 02b42d94 */
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_130 + 0x10))(local_130);
        piVar15 = (int *)((long)local_130 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
                    /* try { // try from 02b3f6f4 to 02c3f723 has its CatchHandler @ 02b41d84 */
          (**(code **)(*local_130 + 0x18))(local_130);
        }
      }
    }
    _ZN5Sfs2X4Util9ByteArray8PositionEl(local_118,0);
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_150,*(undefined8 *)(param_2 + 0x48));
    uVar12 = _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(local_150);
    if (local_148 != (long *)0x0) {
      plVar10 = local_148 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b3f74c to 02c3f77b has its CatchHandler @ 02b41d3c */
        (**(code **)(*local_148 + 0x10))(local_148);
        piVar15 = (int *)((long)local_148 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_148 + 0x18))(local_148);
        }
      }
    }
    if ((uVar12 & 1) == 0) {
      _ZN5Sfs2X4Util9ByteArray9ReadShortERs(local_118,&local_160);
      local_13c = (int)local_160;
    }
    else {
      _ZN5Sfs2X4Util9ByteArray7ReadIntERi(local_118,&local_13c);
    }
    plVar1 = local_78;
    puVar7 = PTR_pthread_create_03bd6b78;
    plVar2 = (long *)local_78[1];
                    /* try { // try from 02b3f7a4 to 02c3f7d3 has its CatchHandler @ 02b41cf4 */
    plVar16 = (long *)*local_78;
    for (plVar10 = plVar16; plVar2 != plVar10; plVar10 = plVar10 + 1) {
                    /* try { // try from 02b3f7fc to 02c3f82b has its CatchHandler @ 02b41ca4 */
      __ptr = (undefined *)(*plVar10 + -0x18);
      if (__ptr != puVar6) {
        piVar15 = (int *)(*plVar10 + -8);
        if (puVar7 == (undefined *)0x0) {
          iVar8 = *piVar15;
          *piVar15 = iVar8 + -1;
        }
        else {
          do {
            iVar8 = *piVar15;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
            if (bVar4) {
              *piVar15 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
        }
        if (iVar8 < 1) {
          _ZdlPv(__ptr);
        }
      }
    }
    plVar1[1] = (long)plVar16;
    FUN_0307c7fc(local_88,0,*(undefined8 *)(*local_88 + -0x18),0);
    plVar10 = (long *)_Znwm(8);
    *plVar10 = (long)(puVar6 + 0x18);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_160,plVar10);
    uVar11 = _Znwm(8);
    FUN_0307a6fc(uVar11,"DataSize is ready: %d bytes",&local_1a0);
                    /* try { // try from 02b3f878 to 02c3f887 has its CatchHandler @ 02b42cd8 */
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_170,uVar11);
    plVar2 = local_158;
    plVar16 = local_168;
    plVar10 = (long *)CONCAT62(uStack_15e,local_160);
    if (local_158 != (long *)0x0) {
      plVar1 = local_158 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    if (local_168 != (long *)0x0) {
      plVar1 = local_168 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
                    /* try { // try from 02b3f8bc to 02c3f8eb has its CatchHandler @ 02b41d80 */
    lVar18 = (long)local_13c;
    lVar13 = *(long *)(*plVar10 + -0x18);
    FUN_0307d194(plVar10,lVar13 + 0x1000,0);
    iVar8 = sprintf((char *)*plVar10,(char *)*local_170,lVar18);
    if (iVar8 < 0) {
      FUN_0307d194(plVar10,lVar13,0);
    }
    else {
      FUN_0307d194(plVar10,lVar13 + iVar8,0);
    }
    if (plVar16 != (long *)0x0) {
      plVar10 = plVar16 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b3f914 to 02c3f943 has its CatchHandler @ 02b41d38 */
        (**(code **)(*plVar16 + 0x10))(plVar16);
        piVar15 = (int *)((long)plVar16 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar16 + 0x18))(plVar16);
        }
      }
    }
    if (plVar2 != (long *)0x0) {
      plVar10 = plVar2 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b3f96c to 02c3f99b has its CatchHandler @ 02b41cf0 */
        (**(code **)(*plVar2 + 0x10))(plVar2);
        piVar15 = (int *)((long)plVar2 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar2 + 0x18))(plVar2);
        }
      }
    }
    plVar10 = local_78;
    if (local_78[1] == local_78[2]) {
      _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_
                (local_78,CONCAT62(uStack_15e,local_160));
    }
    else {
      FUN_0307e06c();
      plVar10[1] = plVar10[1] + 8;
                    /* try { // try from 02b3f9c4 to 02c3f9f3 has its CatchHandler @ 02b41ca0 */
    }
    uVar11 = *(undefined8 *)(param_2 + 0x38);
    local_180 = local_78;
    local_178 = local_70;
    if (local_70 != (long *)0x0) {
      plVar10 = local_70 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = (int)*plVar10 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar11,&local_180);
    plVar10 = local_178;
    if (local_178 != (long *)0x0) {
      plVar16 = local_178 + 1;
      do {
        iVar8 = (int)*plVar16 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar4) {
          *(int *)plVar16 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_178 + 0x10))(local_178);
                    /* try { // try from 02b3fa40 to 02c3fa4f has its CatchHandler @ 02b42c1c */
        piVar15 = (int *)((long)plVar10 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_190,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl(local_190,(long)local_13c);
                    /* try { // try from 02b3fa84 to 02c3fab3 has its CatchHandler @ 02b41d7c */
    if (local_188 != (long *)0x0) {
      plVar10 = local_188 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_188 + 0x10))(local_188);
        piVar15 = (int *)((long)local_188 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_188 + 0x18))(local_188);
        }
      }
    }
                    /* try { // try from 02b3fadc to 02c3fb0b has its CatchHandler @ 02b41d34 */
    uVar11 = _Znwm(0x890);
    _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar11);
    _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(&local_1a0,uVar11);
    uVar11 = *(undefined8 *)(param_2 + 0x48);
    local_1b0 = local_1a0;
    local_1a8 = local_198;
    if (local_198 != (long *)0x0) {
      plVar10 = local_198 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = (int)*plVar10 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEN5boost10shared_ptrINS_4Util9ByteArrayEEE
              (uVar11,&local_1b0);
    plVar10 = local_1a8;
    if (local_1a8 != (long *)0x0) {
      plVar16 = local_1a8 + 1;
      do {
                    /* try { // try from 02b3fb34 to 02c3fb63 has its CatchHandler @ 02b41cec */
        iVar8 = (int)*plVar16 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
        if (bVar4) {
          *(int *)plVar16 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1a8 + 0x10))(local_1a8);
        piVar15 = (int *)((long)plVar10 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),3);
                    /* try { // try from 02b3fb8c to 02c3fbbb has its CatchHandler @ 02b41c9c */
    lVar13 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    if (lVar17 < lVar13) {
      local_1d0 = *param_3;
      local_1c8 = (long *)param_3[1];
      uVar11 = local_1d0;
      if (local_1c8 != (long *)0x0) {
        plVar10 = local_1c8 + 1;
        do {
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
          if (bVar4) {
            *(int *)plVar10 = (int)*plVar10 + 1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        uVar11 = *param_3;
      }
      uVar11 = _ZN5Sfs2X4Util9ByteArray6LengthEv(uVar11);
      _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
                (&local_1c0,uVar11,&local_1d0,lVar17);
      plVar10 = local_1b8;
      uVar11 = local_1c0;
      local_1c0 = 0;
      local_1b8 = (long *)0x0;
      plVar16 = (long *)param_3[1];
      *param_3 = uVar11;
      param_3[1] = plVar10;
      if (plVar16 != (long *)0x0) {
        plVar10 = plVar16 + 1;
        do {
          iVar8 = (int)*plVar10 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
          if (bVar4) {
            *(int *)plVar10 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
                    /* try { // try from 02b3fc08 to 02c3fc17 has its CatchHandler @ 02b42b60 */
          (**(code **)(*plVar16 + 0x10))(plVar16);
          piVar15 = (int *)((long)plVar16 + 0xc);
          do {
            iVar8 = *piVar15;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
            if (bVar4) {
              *piVar15 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
            (**(code **)(*plVar16 + 0x18))(plVar16);
          }
        }
      }
      plVar10 = local_1b8;
      if (local_1b8 != (long *)0x0) {
        plVar16 = local_1b8 + 1;
        do {
          iVar8 = (int)*plVar16 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
          if (bVar4) {
            *(int *)plVar16 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b3fc4c to 02c3fc7b has its CatchHandler @ 02b41d78 */
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*local_1b8 + 0x10))(local_1b8);
          piVar15 = (int *)((long)plVar10 + 0xc);
          do {
            iVar8 = *piVar15;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
            if (bVar4) {
              *piVar15 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
            (**(code **)(*plVar10 + 0x18))(plVar10);
          }
        }
      }
      plVar10 = local_1c8;
      if (local_1c8 != (long *)0x0) {
        plVar16 = local_1c8 + 1;
        do {
          iVar8 = (int)*plVar16 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
          if (bVar4) {
            *(int *)plVar16 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b3fca4 to 02c3fcd3 has its CatchHandler @ 02b41d30 */
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*local_1c8 + 0x10))(local_1c8);
          piVar15 = (int *)((long)plVar10 + 0xc);
          do {
            iVar8 = *piVar15;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
            if (bVar4) {
              *piVar15 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
            (**(code **)(*plVar10 + 0x18))(plVar10);
          }
        }
      }
    }
    else {
      uVar11 = *(undefined8 *)(param_2 + 0x18);
      lVar17 = *(long *)(param_2 + 0x20);
      if (lVar17 != 0) {
        piVar15 = (int *)(lVar17 + 8);
        do {
                    /* try { // try from 02b3fcfc to 02c3fd2b has its CatchHandler @ 02b41ce8 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = *piVar15 + 1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
      }
      plVar10 = (long *)param_3[1];
      *param_3 = uVar11;
      param_3[1] = lVar17;
      if (plVar10 != (long *)0x0) {
        plVar16 = plVar10 + 1;
        do {
          iVar8 = (int)*plVar16 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar16,0x10);
          if (bVar4) {
            *(int *)plVar16 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*plVar10 + 0x10))(plVar10);
          piVar15 = (int *)((long)plVar10 + 0xc);
          do {
            iVar8 = *piVar15;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
            if (bVar4) {
              *piVar15 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
                    /* try { // try from 02b3fd54 to 02c3fd83 has its CatchHandler @ 02b41c98 */
            (**(code **)(*plVar10 + 0x18))(plVar10);
          }
        }
      }
    }
    if (local_198 != (long *)0x0) {
      plVar10 = local_198 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_198 + 0x10))(local_198);
        piVar15 = (int *)((long)local_198 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_198 + 0x18))(local_198);
        }
      }
    }
    if (local_168 != (long *)0x0) {
      plVar10 = local_168 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b3fdd0 to 02c3fddf has its CatchHandler @ 02b42aa4 */
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_168 + 0x10))(local_168);
        piVar15 = (int *)((long)local_168 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_168 + 0x18))(local_168);
        }
      }
    }
                    /* try { // try from 02b3fe14 to 02c3fe43 has its CatchHandler @ 02b41d74 */
    if (local_158 != (long *)0x0) {
      plVar10 = local_158 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_158 + 0x10))(local_158);
        piVar15 = (int *)((long)local_158 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_158 + 0x18))(local_158);
        }
      }
    }
                    /* try { // try from 02b3fe6c to 02c3fe9b has its CatchHandler @ 02b41d2c */
    if (local_110 != (long *)0x0) {
      plVar10 = local_110 + 1;
      do {
        iVar8 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_110 + 0x10))(local_110);
        piVar15 = (int *)((long)local_110 + 0xc);
        do {
          iVar8 = *piVar15;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
          if (bVar4) {
            *piVar15 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_110 + 0x18))(local_110);
        }
      }
    }
  }
                    /* try { // try from 02b3fec4 to 02c3fef3 has its CatchHandler @ 02b41ce4 */
  *param_1 = *param_3;
  uVar11 = param_3[1];
  *param_3 = 0;
  param_3[1] = 0;
  param_1[1] = uVar11;
  if (local_90 != (long *)0x0) {
    plVar10 = local_90 + 1;
    do {
      iVar8 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar15 = (int *)((long)local_90 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02b3ff1c to 02c3ff4b has its CatchHandler @ 02b41c94 */
        (**(code **)(*local_90 + 0x18))(local_90);
      }
    }
  }
  if (local_80 != (long *)0x0) {
    plVar10 = local_80 + 1;
    do {
      iVar8 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar15 = (int *)((long)local_80 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
  if (local_70 != (long *)0x0) {
    plVar10 = local_70 + 1;
    do {
      iVar8 = (int)*plVar10 + -1;
                    /* try { // try from 02b3ff98 to 02c3ffa7 has its CatchHandler @ 02b429e8 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar15 = (int *)((long)local_70 + 0xc);
      do {
        iVar8 = *piVar15;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar15,0x10);
        if (bVar4) {
          *piVar15 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
                    /* try { // try from 02b3ffdc to 02c4000b has its CatchHandler @ 02b41d70 */
  if (*(long *)(lVar5 + 0x28) == local_68) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b40b9c
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 *param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined *puVar6;
  undefined *puVar7;
  int iVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  undefined8 uVar12;
  undefined8 *puVar13;
  long *plVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  undefined *__ptr;
  ulong uVar17;
  int *piVar18;
  code *pcVar19;
  long *plVar20;
  undefined1 auStack_1f8 [40];
  undefined8 local_1d0;
  long *local_1c8;
  undefined *local_1c0;
  long *local_1b8;
  undefined1 auStack_1b0 [8];
  long *local_1a8;
  undefined8 local_1a0;
  long *local_198;
  undefined1 auStack_190 [8];
  long *local_188;
  undefined8 local_180;
  long *local_178;
  undefined8 local_170;
  long *local_168;
  undefined1 auStack_160 [8];
  long *local_158;
  undefined8 local_150;
  long *local_148;
  long *local_140;
  long *local_138;
  undefined1 auStack_130 [8];
  long *local_128;
  undefined8 local_120;
  long *local_118;
  long *local_110;
  long *local_108;
  undefined8 local_100;
  long *local_f8;
  undefined8 local_f0;
  long *local_e8;
  undefined8 *local_e0;
  long *local_d8;
  long *local_d0;
  long *local_c8;
  long *local_c0;
  long *local_b8;
  undefined1 auStack_b0 [8];
  long *local_a8;
  undefined1 auStack_a0 [8];
  long *local_98;
  undefined8 local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  long local_68;
  
                    /* try { // try from 02b40bb0 to 02c40bdf has its CatchHandler @ 02b41cc8 */
  lVar5 = tpidr_el0;
  local_68 = *(long *)(lVar5 + 0x28);
  _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_78,*(undefined8 *)(param_2 + 0x48));
  lVar9 = _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv(local_78);
  _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_88,*(undefined8 *)(param_2 + 0x48));
  lVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_88);
                    /* try { // try from 02b40c08 to 02c40c37 has its CatchHandler @ 02b41c7c */
  if (local_80 != (long *)0x0) {
    plVar14 = local_80 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar18 = (int *)((long)local_80 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
  if (local_70 != (long *)0x0) {
    plVar14 = local_70 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02b40c88 to 02c40c97 has its CatchHandler @ 02b424c0 */
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar18 = (int *)((long)local_70 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  lVar11 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
  uVar12 = _Znwm(0x890);
                    /* try { // try from 02b40ccc to 02c40cfb has its CatchHandler @ 02b41d58 */
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_b0,*param_3);
  _ZN5Sfs2X4Util9ByteArrayC1EN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar12,auStack_b0);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(auStack_a0,uVar12);
  if (local_a8 != (long *)0x0) {
    plVar14 = local_a8 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02b40d24 to 02c40d53 has its CatchHandler @ 02b41d10 */
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar18 = (int *)((long)local_a8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_a8 + 0x18))(local_a8);
      }
    }
  }
  lVar9 = lVar9 - lVar10;
  puVar13 = (undefined8 *)_Znwm(0x18);
  puVar13[1] = 0;
  puVar13[2] = 0;
  *puVar13 = 0;
                    /* try { // try from 02b40d7c to 02c40dab has its CatchHandler @ 02b41cc4 */
  _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_c0,puVar13);
  plVar14 = (long *)_Znwm(8);
  puVar6 = PTR_DAT_03c37adf_1_03bd0478;
  *plVar14 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_d0,plVar14);
  uVar12 = _Znwm(8);
  FUN_0307a6fc(uVar12,"Handling Data: %d, previous state: %d/%d",&local_1c0);
                    /* try { // try from 02b40dd4 to 02c40e03 has its CatchHandler @ 02b41c78 */
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_e0,uVar12);
  plVar2 = local_c8;
  plVar20 = local_d0;
  plVar14 = local_d8;
  if (local_c8 != (long *)0x0) {
    plVar1 = local_c8 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  if (local_d8 != (long *)0x0) {
    plVar1 = local_d8 + 1;
    do {
                    /* try { // try from 02b40e04 to 02c40e2f has its CatchHandler @ 02b3f308 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  uVar12 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
  _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_f0,*(undefined8 *)(param_2 + 0x48));
                    /* try { // try from 02b40e30 to 02c40e3b has its CatchHandler @ 02b424b0 */
  uVar15 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_f0);
                    /* try { // try from 02b40e3c to 02c40e4f has its CatchHandler @ 02b41fc4 */
  _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_100,*(undefined8 *)(param_2 + 0x48));
  uVar16 = _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv(local_100);
                    /* try { // try from 02b40e50 to 02c40e5b has its CatchHandler @ 02b41ef8 */
  lVar10 = *(long *)(*plVar20 + -0x18);
  FUN_0307d194(plVar20,lVar10 + 0x1000,0);
  iVar8 = sprintf((char *)*plVar20,(char *)*local_e0,uVar12,uVar15,uVar16);
  if (iVar8 < 0) {
                    /* try { // try from 02b40ea0 to 02c40ecf has its CatchHandler @ 02b42f70 */
    FUN_0307d194(plVar20,lVar10,0);
  }
  else {
    FUN_0307d194(plVar20,lVar10 + iVar8,0);
  }
  if (local_f8 != (long *)0x0) {
    plVar20 = local_f8 + 1;
    do {
      iVar8 = (int)*plVar20 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
      if (bVar4) {
        *(int *)plVar20 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_f8 + 0x10))(local_f8);
      piVar18 = (int *)((long)local_f8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b40ef4 to 02c40f23 has its CatchHandler @ 02b41c34 */
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_f8 + 0x18))(local_f8);
      }
    }
  }
  if (local_e8 != (long *)0x0) {
    plVar20 = local_e8 + 1;
    do {
      iVar8 = (int)*plVar20 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
      if (bVar4) {
        *(int *)plVar20 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_e8 + 0x10))(local_e8);
      piVar18 = (int *)((long)local_e8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b40f48 to 02c40f77 has its CatchHandler @ 02b41c30 */
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_e8 + 0x18))(local_e8);
      }
    }
  }
  if (plVar14 != (long *)0x0) {
    plVar20 = plVar14 + 1;
    do {
      iVar8 = (int)*plVar20 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
      if (bVar4) {
        *(int *)plVar20 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b40f78 to 02c40f83 has its CatchHandler @ 02b41ee8 */
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar14 + 0x10))(plVar14);
      piVar18 = (int *)((long)plVar14 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b40fa4 to 02c40faf has its CatchHandler @ 02b41e6c */
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar14 + 0x18))(plVar14);
      }
    }
  }
  if (plVar2 != (long *)0x0) {
                    /* try { // try from 02b40fbc to 02c40fc7 has its CatchHandler @ 02b41df4 */
    plVar14 = plVar2 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar2 + 0x10))(plVar2);
      piVar18 = (int *)((long)plVar2 + 0xc);
      do {
        iVar8 = *piVar18;
                    /* try { // try from 02b40ff0 to 02c4101f has its CatchHandler @ 02b42f6c */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar2 + 0x18))(plVar2);
      }
    }
  }
  plVar14 = local_c0;
  if (local_c0[1] == local_c0[2]) {
    _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_c0,local_d0);
  }
  else {
                    /* try { // try from 02b41020 to 02c4103b has its CatchHandler @ 02b3f308 */
    FUN_0307e06c();
    plVar14[1] = plVar14[1] + 8;
  }
                    /* try { // try from 02b4103c to 02c4104f has its CatchHandler @ 02b41d90 */
  uVar12 = *(undefined8 *)(param_2 + 0x38);
  local_110 = local_c0;
  local_108 = local_b8;
  if (local_b8 != (long *)0x0) {
    plVar14 = local_b8 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = (int)*plVar14 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar12,&local_110);
  plVar14 = local_108;
  if (local_108 != (long *)0x0) {
    plVar20 = local_108 + 1;
    do {
      iVar8 = (int)*plVar20 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
      if (bVar4) {
        *(int *)plVar20 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_108 + 0x10))(local_108);
                    /* try { // try from 02b41098 to 02c410a7 has its CatchHandler @ 02b423f4 */
      piVar18 = (int *)((long)plVar14 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar14 + 0x18))(plVar14);
      }
    }
  }
  lVar10 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
  if (lVar10 < lVar9) {
                    /* try { // try from 02b410dc to 02c4110b has its CatchHandler @ 02b41d54 */
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_1a0,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_1b0,*param_3);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEE
              (local_1a0,auStack_1b0);
    if (local_1a8 != (long *)0x0) {
      plVar14 = local_1a8 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1a8 + 0x10))(local_1a8);
        piVar18 = (int *)((long)local_1a8 + 0xc);
        do {
          iVar8 = *piVar18;
                    /* try { // try from 02b41134 to 02c41163 has its CatchHandler @ 02b41d0c */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_1a8 + 0x18))(local_1a8);
        }
      }
    }
    if (local_198 != (long *)0x0) {
      plVar14 = local_198 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_198 + 0x10))(local_198);
        piVar18 = (int *)((long)local_198 + 0xc);
        do {
          iVar8 = *piVar18;
                    /* try { // try from 02b4118c to 02c411bb has its CatchHandler @ 02b41cc0 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_198 + 0x18))(local_198);
        }
      }
    }
  }
  else {
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_120,*(undefined8 *)(param_2 + 0x48));
    _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_130,*param_3);
    _ZN5Sfs2X4Util9ByteArray10WriteBytesEN5boost10shared_ptrISt6vectorIhSaIhEEEEll
              (local_120,auStack_130,0,lVar9);
    if (local_128 != (long *)0x0) {
                    /* try { // try from 02b411e4 to 02c41213 has its CatchHandler @ 02b41c74 */
      plVar14 = local_128 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_128 + 0x10))(local_128);
        piVar18 = (int *)((long)local_128 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_128 + 0x18))(local_128);
        }
      }
    }
    if (local_118 != (long *)0x0) {
      plVar14 = local_118 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_118 + 0x10))(local_118);
                    /* try { // try from 02b41264 to 02c41273 has its CatchHandler @ 02b42338 */
        piVar18 = (int *)((long)local_118 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_118 + 0x18))(local_118);
        }
      }
    }
    plVar1 = local_c0;
    puVar7 = PTR_pthread_create_03bd6b78;
    plVar2 = (long *)local_c0[1];
    plVar20 = (long *)*local_c0;
    for (plVar14 = plVar20; plVar2 != plVar14; plVar14 = plVar14 + 1) {
      __ptr = (undefined *)(*plVar14 + -0x18);
      if (__ptr != puVar6) {
        piVar18 = (int *)(*plVar14 + -8);
        if (puVar7 == (undefined *)0x0) {
          iVar8 = *piVar18;
          *piVar18 = iVar8 + -1;
        }
        else {
          do {
            iVar8 = *piVar18;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
            if (bVar4) {
              *piVar18 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
        }
        if (iVar8 < 1) {
          _ZdlPv(__ptr);
        }
      }
                    /* try { // try from 02b41300 to 02c4132f has its CatchHandler @ 02b41d08 */
    }
    plVar1[1] = (long)plVar20;
    FUN_0307c7fc(local_d0,0,*(undefined8 *)(*local_d0 + -0x18),0);
    plVar14 = local_c0;
    FUN_0307a6fc(&local_1c0,"<<< Packet Complete >>>",auStack_1f8);
    puVar13 = (undefined8 *)plVar14[1];
    if (puVar13 == (undefined8 *)plVar14[2]) {
      _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJSsEEEvDpOT_(plVar14,&local_1c0);
    }
    else {
      *puVar13 = local_1c0;
      plVar14[1] = (long)(puVar13 + 1);
      local_1c0 = puVar6 + 0x18;
                    /* try { // try from 02b41358 to 02c41387 has its CatchHandler @ 02b41cbc */
    }
    if (local_1c0 + -0x18 != puVar6) {
      piVar18 = (int *)(local_1c0 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar8 = *piVar18;
                    /* try { // try from 02b419f8 to 02c41a03 has its CatchHandler @ 02b42040 */
        *piVar18 = iVar8 + -1;
      }
      else {
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
      }
                    /* try { // try from 02b41a04 to 02c41a13 has its CatchHandler @ 02b41efc */
      if (iVar8 < 1) {
        _ZdlPv(local_1c0 + -0x18);
      }
    }
    uVar12 = *(undefined8 *)(param_2 + 0x38);
    local_140 = local_c0;
    local_138 = local_b8;
    if (local_b8 != (long *)0x0) {
      plVar14 = local_b8 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = (int)*plVar14 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X7Logging6Logger5DebugEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar12,&local_140);
    plVar14 = local_138;
    if (local_138 != (long *)0x0) {
      plVar20 = local_138 + 1;
      do {
                    /* try { // try from 02b413b0 to 02c413df has its CatchHandler @ 02b41c70 */
        iVar8 = (int)*plVar20 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
        if (bVar4) {
          *(int *)plVar20 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_138 + 0x10))(local_138);
        piVar18 = (int *)((long)plVar14 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar14 + 0x18))(plVar14);
        }
      }
    }
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_150,*(undefined8 *)(param_2 + 0x48));
    uVar17 = _ZN5Sfs2X4Core12PacketHeader9EncryptedEv(local_150);
    if (local_148 != (long *)0x0) {
      plVar14 = local_148 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
                    /* try { // try from 02b41434 to 02c4143f has its CatchHandler @ 02b42278 */
                    /* try { // try from 02b41440 to 02c4144f has its CatchHandler @ 02b41f60 */
        (**(code **)(*local_148 + 0x10))(local_148);
        piVar18 = (int *)((long)local_148 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_148 + 0x18))(local_148);
        }
      }
    }
    if ((uVar17 & 1) != 0) {
      plVar14 = *(long **)(param_2 + 0x80);
      pcVar19 = *(code **)(*plVar14 + 8);
                    /* try { // try from 02b41484 to 02c414b3 has its CatchHandler @ 02b41cb8 */
      _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(auStack_160,*(undefined8 *)(param_2 + 0x48));
      (*pcVar19)(plVar14,auStack_160);
      if (local_158 != (long *)0x0) {
        plVar14 = local_158 + 1;
        do {
          iVar8 = (int)*plVar14 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
          if (bVar4) {
            *(int *)plVar14 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*local_158 + 0x10))(local_158);
          piVar18 = (int *)((long)local_158 + 0xc);
          do {
            iVar8 = *piVar18;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
            if (bVar4) {
              *piVar18 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
                    /* try { // try from 02b414dc to 02c4150b has its CatchHandler @ 02b41c60 */
            (**(code **)(*local_158 + 0x18))(local_158);
          }
        }
      }
    }
    _ZN5Sfs2X8Bitswarm13PendingPacket6HeaderEv(&local_170,*(undefined8 *)(param_2 + 0x48));
    uVar17 = _ZN5Sfs2X4Core12PacketHeader10CompressedEv(local_170);
    if (local_168 != (long *)0x0) {
      plVar14 = local_168 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_168 + 0x10))(local_168);
                    /* try { // try from 02b41534 to 02c41563 has its CatchHandler @ 02b41c54 */
        piVar18 = (int *)((long)local_168 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_168 + 0x18))(local_168);
        }
      }
    }
    if ((uVar17 & 1) != 0) {
      _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(&local_180,*(undefined8 *)(param_2 + 0x48));
      _ZN5Sfs2X4Util9ByteArray10UncompressEv(local_180);
      if (local_178 != (long *)0x0) {
        plVar14 = local_178 + 1;
        do {
          iVar8 = (int)*plVar14 + -1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
          if (bVar4) {
            *(int *)plVar14 = iVar8;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b4158c to 02c415bb has its CatchHandler @ 02b41c48 */
        } while (cVar3 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*local_178 + 0x10))(local_178);
          piVar18 = (int *)((long)local_178 + 0xc);
          do {
            iVar8 = *piVar18;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
            if (bVar4) {
              *piVar18 = iVar8 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar8 + -1 == 0) {
            (**(code **)(*local_178 + 0x18))(local_178);
          }
        }
      }
    }
    plVar14 = *(long **)(param_2 + 0x58);
    pcVar19 = *(code **)(*plVar14 + 8);
    _ZN5Sfs2X8Bitswarm13PendingPacket6BufferEv(auStack_190,*(undefined8 *)(param_2 + 0x48));
                    /* try { // try from 02b415e4 to 02c41613 has its CatchHandler @ 02b41c3c */
    (*pcVar19)(plVar14,auStack_190);
    if (local_188 != (long *)0x0) {
      plVar14 = local_188 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_188 + 0x10))(local_188);
        piVar18 = (int *)((long)local_188 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*local_188 + 0x18))(local_188);
        }
      }
    }
    _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),4);
  }
  if (lVar9 < lVar11) {
                    /* try { // try from 02b41660 to 02c4166f has its CatchHandler @ 02b421bc */
    local_1d0 = *param_3;
    local_1c8 = (long *)param_3[1];
    uVar12 = local_1d0;
    if (local_1c8 != (long *)0x0) {
      plVar14 = local_1c8 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = (int)*plVar14 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      uVar12 = *param_3;
    }
    uVar12 = _ZN5Sfs2X4Util9ByteArray6LengthEv(uVar12);
    _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
              (&local_1c0,uVar12,&local_1d0,lVar9);
    plVar14 = local_1b8;
    puVar6 = local_1c0;
    local_1c0 = (undefined *)0x0;
    local_1b8 = (long *)0x0;
    plVar20 = (long *)param_3[1];
                    /* try { // try from 02b416a4 to 02c416d3 has its CatchHandler @ 02b41d4c */
    *param_3 = puVar6;
    param_3[1] = plVar14;
    if (plVar20 != (long *)0x0) {
      plVar14 = plVar20 + 1;
      do {
        iVar8 = (int)*plVar14 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar4) {
          *(int *)plVar14 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar20 + 0x10))(plVar20);
        piVar18 = (int *)((long)plVar20 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar20 + 0x18))(plVar20);
        }
      }
    }
                    /* try { // try from 02b416fc to 02c4172b has its CatchHandler @ 02b41d04 */
    plVar14 = local_1b8;
    if (local_1b8 != (long *)0x0) {
      plVar20 = local_1b8 + 1;
      do {
        iVar8 = (int)*plVar20 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
        if (bVar4) {
          *(int *)plVar20 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1b8 + 0x10))(local_1b8);
        piVar18 = (int *)((long)plVar14 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar14 + 0x18))(plVar14);
        }
      }
    }
                    /* try { // try from 02b41754 to 02c41783 has its CatchHandler @ 02b41cb4 */
    plVar14 = local_1c8;
    if (local_1c8 != (long *)0x0) {
      plVar20 = local_1c8 + 1;
      do {
        iVar8 = (int)*plVar20 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
        if (bVar4) {
          *(int *)plVar20 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*local_1c8 + 0x10))(local_1c8);
        piVar18 = (int *)((long)plVar14 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar14 + 0x18))(plVar14);
                    /* try { // try from 02b417ac to 02c417db has its CatchHandler @ 02b41c6c */
        }
      }
    }
  }
  else {
    uVar12 = *(undefined8 *)(param_2 + 0x18);
    lVar9 = *(long *)(param_2 + 0x20);
    if (lVar9 != 0) {
      piVar18 = (int *)(lVar9 + 8);
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = *piVar18 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plVar14 = (long *)param_3[1];
    *param_3 = uVar12;
    param_3[1] = lVar9;
    if (plVar14 != (long *)0x0) {
      plVar20 = plVar14 + 1;
      do {
        iVar8 = (int)*plVar20 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar20,0x10);
        if (bVar4) {
          *(int *)plVar20 = iVar8;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar14 + 0x10))(plVar14);
        piVar18 = (int *)((long)plVar14 + 0xc);
        do {
          iVar8 = *piVar18;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
          if (bVar4) {
            *piVar18 = iVar8 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar14 + 0x18))(plVar14);
        }
      }
    }
  }
                    /* try { // try from 02b41828 to 02c41837 has its CatchHandler @ 02b42100 */
  if (local_d8 != (long *)0x0) {
    plVar14 = local_d8 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar18 = (int *)((long)local_d8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b4186c to 02c4189b has its CatchHandler @ 02b41d48 */
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_d8 + 0x18))(local_d8);
      }
    }
  }
  if (local_c8 != (long *)0x0) {
    plVar14 = local_c8 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar18 = (int *)((long)local_c8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b418c4 to 02c418f3 has its CatchHandler @ 02b41d00 */
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_c8 + 0x18))(local_c8);
      }
    }
  }
  if (local_b8 != (long *)0x0) {
    plVar14 = local_b8 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_b8 + 0x10))(local_b8);
      piVar18 = (int *)((long)local_b8 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b4191c to 02c4194b has its CatchHandler @ 02b41cb0 */
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_b8 + 0x18))(local_b8);
      }
    }
  }
  uVar15 = param_3[1];
  uVar12 = *param_3;
  param_3[1] = 0;
  param_1[1] = uVar15;
  *param_1 = uVar12;
  *param_3 = 0;
  if (local_98 != (long *)0x0) {
    plVar14 = local_98 + 1;
    do {
      iVar8 = (int)*plVar14 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar4) {
        *(int *)plVar14 = iVar8;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
                    /* try { // try from 02b41974 to 02c419a3 has its CatchHandler @ 02b41c68 */
      piVar18 = (int *)((long)local_98 + 0xc);
      do {
        iVar8 = *piVar18;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar18,0x10);
        if (bVar4) {
          *piVar18 = iVar8 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*local_98 + 0x18))(local_98);
      }
    }
  }
  if (*(long *)(lVar5 + 0x28) == local_68) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b42b00
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler17HandleInvalidDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 *param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long lVar7;
  undefined8 uVar8;
  long lVar9;
  long *plVar10;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02b42b24 to 02c42b53 has its CatchHandler @ 02b42b5c */
  if (*(long *)(param_2 + 0x68) == 0) {
    _ZN5Sfs2X3FSM18FiniteStateMachine15ApplyTransitionEl(*(undefined8 *)(param_2 + 0x70),6);
                    /* catch() { ... } // from try @ 02b42c44 with catch @ 02b42cd0 */
    *param_1 = *param_3;
                    /* catch() { ... } // from try @ 02b42c9c with catch @ 02b42cd4 */
    param_1[1] = 0;
  }
  else {
    lVar7 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    lVar9 = *(long *)(param_2 + 0x68);
    if (lVar7 < lVar9) {
      lVar9 = _ZN5Sfs2X4Util9ByteArray6LengthEv(*param_3);
    }
                    /* catch() { ... } // from try @ 02b42acc with catch @ 02b42b58 */
    local_68 = *param_3;
    local_60 = (long *)param_3[1];
                    /* catch() { ... } // from try @ 02b42b24 with catch @ 02b42b5c */
                    /* catch() { ... } // from try @ 02b3fc08 with catch @ 02b42b60 */
    uVar8 = local_68;
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
      uVar8 = *param_3;
    }
    uVar8 = _ZN5Sfs2X4Util9ByteArray6LengthEv(uVar8);
                    /* try { // try from 02b42b88 to 02c42bb7 has its CatchHandler @ 02b42c14 */
    _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
              (&local_58,uVar8,&local_68,lVar9);
    plVar1 = local_50;
    uVar8 = local_58;
    local_58 = 0;
    local_50 = (long *)0x0;
    plVar10 = (long *)param_3[1];
    *param_3 = uVar8;
    param_3[1] = plVar1;
    if (plVar10 != (long *)0x0) {
      plVar1 = plVar10 + 1;
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
        (**(code **)(*plVar10 + 0x10))(plVar10);
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
                    /* try { // try from 02b42be0 to 02c42c0f has its CatchHandler @ 02b42c18 */
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    plVar1 = local_50;
    if (local_50 != (long *)0x0) {
      plVar10 = local_50 + 1;
      do {
        iVar5 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
                    /* catch() { ... } // from try @ 02b42b88 with catch @ 02b42c14 */
                    /* catch() { ... } // from try @ 02b42be0 with catch @ 02b42c18 */
                    /* catch() { ... } // from try @ 02b3fa40 with catch @ 02b42c1c */
        (**(code **)(*local_50 + 0x10))(local_50);
        piVar2 = (int *)((long)plVar1 + 0xc);
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
                    /* try { // try from 02b42c44 to 02c42c73 has its CatchHandler @ 02b42cd0 */
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
    plVar1 = local_60;
    if (local_60 != (long *)0x0) {
      plVar10 = local_60 + 1;
      do {
        iVar5 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
        (**(code **)(*local_60 + 0x10))(local_60);
        piVar2 = (int *)((long)plVar1 + 0xc);
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
                    /* try { // try from 02b42c9c to 02c42ccb has its CatchHandler @ 02b42cd4 */
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
    *(long *)(param_2 + 0x68) = *(long *)(param_2 + 0x68) - lVar9;
    *param_1 = *param_3;
    param_1[1] = 0;
  }
                    /* catch() { ... } // from try @ 02b3f878 with catch @ 02b42cd8 */
  uVar8 = param_3[1];
  *param_3 = 0;
  param_3[1] = 0;
  param_1[1] = uVar8;
  if (*(long *)(lVar6 + 0x28) == local_48) {
                    /* try { // try from 02b42d00 to 02c42d2f has its CatchHandler @ 02b42d8c */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
// ADDRESS : 02b42d80
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler15ResizeByteArrayEN5boost10shared_ptrINS_4Util9ByteArrayEEEll
               (undefined8 param_1,undefined8 param_2,undefined8 *param_3,long param_4)

{
  long *plVar1;
  int *piVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 *puVar8;
  undefined8 uVar9;
  long lVar10;
  undefined8 *local_a0;
  long *local_98;
  long local_90;
  long *local_88;
  undefined8 *local_80;
  long *local_78;
  long *local_70;
  long *plStack_68;
  long *local_60;
  long local_58;
  
                    /* catch() { ... } // from try @ 02b42d00 with catch @ 02b42d8c */
                    /* catch() { ... } // from try @ 02b42d58 with catch @ 02b42d90 */
                    /* catch() { ... } // from try @ 02b3f6b0 with catch @ 02b42d94 */
  lVar7 = tpidr_el0;
  local_58 = *(long *)(lVar7 + 0x28);
                    /* try { // try from 02b42dbc to 02c42deb has its CatchHandler @ 02b42e48 */
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_70,*param_3);
  lVar10 = *local_70;
  if (plStack_68 != (long *)0x0) {
    plVar1 = plStack_68 + 1;
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
      (**(code **)(*plStack_68 + 0x10))(plStack_68);
      piVar2 = (int *)((long)plStack_68 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b42e14 to 02c42e43 has its CatchHandler @ 02b42e4c */
        (**(code **)(*plStack_68 + 0x18))(plStack_68);
      }
    }
  }
  puVar8 = (undefined8 *)_Znwm(0x18);
  puVar8[1] = 0;
  puVar8[2] = 0;
  *puVar8 = 0;
  local_78 = (long *)0x0;
  local_80 = puVar8;
  _ZN5boost6detail12shared_countC2ISt6vectorIhSaIhEEEEPT_(&local_60,puVar8);
  plVar1 = local_78;
                    /* catch() { ... } // from try @ 02b42dbc with catch @ 02b42e48 */
  local_78 = local_60;
                    /* catch() { ... } // from try @ 02b42e14 with catch @ 02b42e4c */
  local_60 = plVar1;
                    /* catch() { ... } // from try @ 02b3f4e8 with catch @ 02b42e50 */
  if (plVar1 != (long *)0x0) {
    plVar3 = plVar1 + 1;
    do {
      iVar6 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b42e78 to 02c42ea7 has its CatchHandler @ 02b42f04 */
      (**(code **)(*plVar1 + 0x10))(plVar1);
      piVar2 = (int *)((long)plVar1 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_80,puVar8,puVar8);
  puVar8 = local_80;
  uVar9 = *local_80;
  _ZN5Sfs2X4Util9ByteArray5BytesEv(&local_90,*param_3);
                    /* try { // try from 02b42ed0 to 02c42eff has its CatchHandler @ 02b42f08 */
  _ZNSt6vectorIhSaIhEE15_M_range_insertIN9__gnu_cxx17__normal_iteratorIPhS1_EEEEvS6_T_S7_St20forward_iterator_tag
            (puVar8,uVar9,lVar10 + param_4,*(undefined8 *)(local_90 + 8));
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
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
                    /* catch() { ... } // from try @ 02b42e78 with catch @ 02b42f04 */
                    /* catch() { ... } // from try @ 02b42ed0 with catch @ 02b42f08 */
                    /* catch() { ... } // from try @ 02b3f37c with catch @ 02b42f0c */
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar2 = (int *)((long)local_88 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b42f34 to 02c42f63 has its CatchHandler @ 02b42f68 */
        (**(code **)(*local_88 + 0x18))(local_88);
      }
    }
  }
  uVar9 = _Znwm(0x890);
  local_a0 = local_80;
  local_98 = local_78;
  if (local_78 != (long *)0x0) {
    plVar1 = local_78 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* catch() { ... } // from try @ 02b42f34 with catch @ 02b42f68 */
                    /* catch() { ... } // from try @ 02b40ff0 with catch @ 02b42f6c */
                    /* catch() { ... } // from try @ 02b40ea0 with catch @ 02b42f70
                       catch() { ... } // from try @ 02b41c18 with catch @ 02b42f70 */
  _ZN5Sfs2X4Util9ByteArrayC1EN5boost10shared_ptrISt6vectorIhSaIhEEEE(uVar9,&local_a0);
  _ZN5boost10shared_ptrIN5Sfs2X4Util9ByteArrayEEC2IS3_EEPT_(param_1,uVar9);
  plVar1 = local_98;
  if (local_98 != (long *)0x0) {
    plVar3 = local_98 + 1;
    do {
      iVar6 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
                    /* try { // try from 02b42fa4 to 02c42fcf has its CatchHandler @ 02b430e0 */
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar2 = (int *)((long)plVar1 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  plVar1 = local_78;
  if (local_78 != (long *)0x0) {
    plVar3 = local_78 + 1;
    do {
      iVar6 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b42ff4 to 02c43023 has its CatchHandler @ 02b430dc */
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar2 = (int *)((long)plVar1 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_58) {
                    /* try { // try from 02b4304c to 02c4307b has its CatchHandler @ 02b430e4 */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
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
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler8WriteUDPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b43a60
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler8WriteUDPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  long *plVar2;
  int *piVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  code *pcVar8;
  undefined8 local_48;
  long *local_40;
  long *local_38;
  long *local_30;
  long local_28;
  
                    /* try { // try from 02b43a6c to 02c43a9b has its CatchHandler @ 02b43c9c */
  lVar7 = tpidr_el0;
  local_28 = *(long *)(lVar7 + 0x28);
  _ZN5Sfs2X8Bitswarm14BitSwarmClient10UdpManagerEv(&local_38,*(undefined8 *)(param_1 + 0x28));
  local_48 = *param_2;
  pcVar8 = *(code **)(*local_38 + 0x18);
  local_40 = (long *)param_2[1];
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b43ac0 to 02c43aef has its CatchHandler @ 02b43c98 */
  (*pcVar8)(local_38,&local_48);
  plVar1 = local_40;
  if (local_40 != (long *)0x0) {
    plVar2 = local_40 + 1;
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
                    /* try { // try from 02b43af0 to 02c43afb has its CatchHandler @ 02b43dfc */
      (**(code **)(*local_40 + 0x10))(local_40);
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
                    /* try { // try from 02b43b1c to 02c43b27 has its CatchHandler @ 02b43d80 */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (local_30 != (long *)0x0) {
    plVar1 = local_30 + 1;
    do {
      iVar6 = (int)*plVar1 + -1;
                    /* try { // try from 02b43b34 to 02c43b3f has its CatchHandler @ 02b43d08 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_30 + 0x10))(local_30);
      piVar3 = (int *)((long)local_30 + 0xc);
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
                    /* try { // try from 02b43b68 to 02c43b97 has its CatchHandler @ 02b43e98 */
        (**(code **)(*local_30 + 0x18))(local_30);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_28) {
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b43b98 to 02c43bb3 has its CatchHandler @ 02b43934 */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b43c68
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  code *pcVar7;
  undefined1 auStack_58 [8];
  long *local_50;
  long *local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
                    /* try { // try from 02b43c80 to 02c43c8f has its CatchHandler @ 02b43e9c */
  local_38 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02b43c90 to 02c43ccf has its CatchHandler @ 02b43934 */
  _ZN5Sfs2X8Bitswarm14BitSwarmClient6SocketEv(&local_48,*(undefined8 *)(param_1 + 0x28));
                    /* catch() { ... } // from try @ 02b43ac0 with catch @ 02b43c98 */
                    /* catch() { ... } // from try @ 02b43a6c with catch @ 02b43c9c */
                    /* catch() { ... } // from try @ 02b43c28 with catch @ 02b43ca0 */
                    /* catch() { ... } // from try @ 02b43bb4 with catch @ 02b43ca4 */
  pcVar7 = *(code **)(*local_48 + 0x40);
  _ZN5Sfs2X4Util9ByteArray5BytesEv(auStack_58,*param_2);
  (*pcVar7)(local_48,auStack_58);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      iVar5 = (int)*plVar1 + -1;
                    /* try { // try from 02b43cd0 to 02c43cff has its CatchHandler @ 02b43d04 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)local_50 + 0xc);
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
                    /* catch() { ... } // from try @ 02b43cd0 with catch @ 02b43d04 */
                    /* catch() { ... } // from try @ 02b43b34 with catch @ 02b43d08 */
        (**(code **)(*local_50 + 0x18))(local_50);
      }
    }
  }
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
                    /* try { // try from 02b43d38 to 02c43d6b has its CatchHandler @ 02b43d7c */
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)local_40 + 0xc);
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
        (**(code **)(*local_40 + 0x18))(local_40);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
                    /* catch() { ... } // from try @ 02b43d38 with catch @ 02b43d7c */
                    /* catch() { ... } // from try @ 02b43b1c with catch @ 02b43d80 */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12SFSIOHandler11OnDataWriteEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 02b43e68
================================================================

void _ZN5Sfs2X4Core12SFSIOHandler11OnDataWriteEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  long *plVar2;
  long *plVar3;
  long *plVar4;
  char cVar5;
  bool bVar6;
  byte bVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  long lVar14;
  long *plVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  undefined8 *puVar18;
  ulong uVar19;
  long lVar20;
  byte *local_1b0;
  long *local_1a8;
  undefined8 local_1a0;
  long *local_198;
  undefined8 local_190;
  long *local_188;
  undefined8 *local_180;
  long *local_178;
  undefined8 local_170;
  long *local_168;
  byte *local_160;
  long *local_158;
  undefined8 *local_150;
  long *local_148;
  long local_140;
  long *local_138;
  long *local_130;
  long *local_128;
  undefined8 *local_120;
  long *local_118;
  undefined8 *local_110;
  long *local_108;
  long *local_100;
  long *local_f8;
  long local_f0;
  long *local_e8;
  undefined8 local_e0;
  long *local_d8;
  long *local_d0;
  long *local_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 *local_a8;
  long *plStack_a0;
  long *local_98;
  long *local_90;
  long *local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  long local_68;
  
                    /* catch() { ... } // from try @ 02b43e50 with catch @ 02b43e84 */
                    /* catch() { ... } // from try @ 02b4399c with catch @ 02b43e88 */
  lVar20 = tpidr_el0;
  local_68 = *(long *)(lVar20 + 0x28);
                    /* catch() { ... } // from try @ 02b43b68 with catch @ 02b43e98 */
                    /* catch() { ... } // from try @ 02b43a04 with catch @ 02b43e9c
                       catch() { ... } // from try @ 02b43c80 with catch @ 02b43e9c */
  (**(code **)(*(long *)*param_2 + 0x10))(&local_88,(long *)*param_2);
  (**(code **)(*local_88 + 0x40))(&local_78);
                    /* try { // try from 02b43ec8 to 02c43ef7 has its CatchHandler @ 02b44008 */
  if (local_80 != (long *)0x0) {
    plVar15 = local_80 + 1;
    do {
      iVar9 = (int)*plVar15 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_80 + 0x10))(local_80);
      piVar1 = (int *)((long)local_80 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_80 + 0x18))(local_80);
      }
    }
  }
                    /* try { // try from 02b43f20 to 02c43f4b has its CatchHandler @ 02b44004 */
  lVar11 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_78);
  lVar12 = _ZN5Sfs2X8Bitswarm14BitSwarmClient20CompressionThresholdEv
                     (*(undefined8 *)(param_1 + 0x28));
  _ZN5Sfs2X8Bitswarm14BitSwarmClient9CryptoKeyEv(&local_98,*(undefined8 *)(param_1 + 0x28));
  if (local_98 == (long *)0x0) {
    uVar8 = 0;
    plVar15 = local_90;
  }
  else {
    uVar8 = _ZN5Sfs2X8Bitswarm14BitSwarmClient14IsReconnectingEv(*(undefined8 *)(param_1 + 0x28));
    uVar8 = uVar8 ^ 1;
    plVar15 = local_90;
  }
  local_90 = plVar15;
  if (plVar15 != (long *)0x0) {
    plVar2 = plVar15 + 1;
    do {
                    /* try { // try from 02b43f74 to 02c43fa3 has its CatchHandler @ 02b4400c */
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar15 + 0x10))(plVar15);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  lVar13 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_78);
                    /* try { // try from 02b43fcc to 02c43ffb has its CatchHandler @ 02b44010 */
  lVar14 = _ZN5Sfs2X8Bitswarm14BitSwarmClient14MaxMessageSizeEv(*(undefined8 *)(param_1 + 0x28));
  if (lVar14 < lVar13) {
    plVar15 = (long *)_Znwm(8);
    *plVar15 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
                    /* try { // try from 02b43ffc to 02c44013 has its CatchHandler @ 02b43934 */
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_98,plVar15);
                    /* catch() { ... } // from try @ 02b43f20 with catch @ 02b44004 */
                    /* catch() { ... } // from try @ 02b43ec8 with catch @ 02b44008 */
    uVar16 = _Znwm(8);
                    /* catch() { ... } // from try @ 02b43f74 with catch @ 02b4400c */
                    /* catch() { ... } // from try @ 02b43fcc with catch @ 02b44010 */
    FUN_0307a6fc(uVar16,"Message size is too big: %d, the server limit is: %d",&local_c0);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_a8,uVar16);
    plVar2 = local_90;
    plVar15 = local_98;
    if (local_90 != (long *)0x0) {
      plVar3 = local_90 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar3,0x10);
        if (bVar6) {
          *(int *)plVar3 = (int)*plVar3 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b44048 to 02c44077 has its CatchHandler @ 02b44084 */
      } while (cVar5 != '\0');
    }
    if (plStack_a0 != (long *)0x0) {
      plVar3 = plStack_a0 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar3,0x10);
        if (bVar6) {
          *(int *)plVar3 = (int)*plVar3 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    uVar16 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_78);
    uVar17 = _ZN5Sfs2X8Bitswarm14BitSwarmClient14MaxMessageSizeEv(*(undefined8 *)(param_1 + 0x28));
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b44048 with catch @ 02b44084
                        */
    lVar20 = *(long *)(*plVar15 + -0x18);
                    /* try { // try from 02b44088 to 02c440cb has its CatchHandler @ 02b44088
                       catch() { ... } // from try @ 02b44088 with catch @ 02b44088
                       catch() { ... } // from try @ 02b446e0 with catch @ 02b44088
                       catch() { ... } // from try @ 02b44930 with catch @ 02b44088
                       catch() { ... } // from try @ 02b44b28 with catch @ 02b44088
                       catch() { ... } // from try @ 02b44b58 with catch @ 02b44088
                       catch() { ... } // from try @ 02b456f0 with catch @ 02b44088
                       catch() { ... } // from try @ 02b4572c with catch @ 02b44088
                       catch() { ... } // from try @ 02b4587c with catch @ 02b44088 */
    FUN_0307d194(plVar15,lVar20 + 0x1000,0);
    iVar9 = sprintf((char *)*plVar15,(char *)*local_a8,uVar16,uVar17);
    if (iVar9 < 0) {
      FUN_0307d194(plVar15,lVar20,0);
    }
    else {
      FUN_0307d194(plVar15,lVar20 + iVar9,0);
    }
    if (plStack_a0 != (long *)0x0) {
      plVar15 = plStack_a0 + 1;
      do {
                    /* try { // try from 02b440cc to 02c440d3 has its CatchHandler @ 02b454bc */
        iVar9 = (int)*plVar15 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b440e4 to 02c440eb has its CatchHandler @ 02b45348 */
        (**(code **)(*plStack_a0 + 0x10))(plStack_a0);
        piVar1 = (int *)((long)plStack_a0 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plStack_a0 + 0x18))(plStack_a0);
        }
      }
    }
                    /* try { // try from 02b44114 to 02c4411f has its CatchHandler @ 02b45690 */
    if (plVar2 != (long *)0x0) {
      plVar15 = plVar2 + 1;
      do {
                    /* try { // try from 02b44120 to 02c4412b has its CatchHandler @ 02b45600 */
        iVar9 = (int)*plVar15 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
                    /* try { // try from 02b4412c to 02c44137 has its CatchHandler @ 02b45690 */
      if (iVar9 == 0) {
        (**(code **)(*plVar2 + 0x10))(plVar2);
        piVar1 = (int *)((long)plVar2 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar2 + 0x18))(plVar2);
        }
      }
    }
    local_c0 = _Znwm(0x38);
    local_d0 = local_98;
    local_c8 = local_90;
    if (local_90 != (long *)0x0) {
      local_90 = local_90 + 1;
      do {
                    /* try { // try from 02b44184 to 02c4418f has its CatchHandler @ 02b454e0 */
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(local_90,0x10);
        if (bVar6) {
          *(int *)local_90 = (int)*local_90 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    _ZN5Sfs2X10Exceptions13SFSCodecErrorC1EN5boost10shared_ptrISsEE(local_c0,&local_d0);
    uStack_b8 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions13SFSCodecErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_c0,local_c0,(ulong)&local_c0 | 8);
    plVar15 = local_c8;
                    /* try { // try from 02b441b8 to 02c441e7 has its CatchHandler @ 02b454d8 */
    if (local_c8 != (long *)0x0) {
      plVar2 = local_c8 + 1;
      do {
        iVar9 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_c8 + 0x10))(local_c8);
        piVar1 = (int *)((long)plVar15 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar15 + 0x18))(plVar15);
        }
      }
    }
                    /* try { // try from 02b44210 to 02c4423f has its CatchHandler @ 02b454d4 */
    puVar18 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar16 = uStack_b8;
    puVar18[1] = 0;
    uStack_b8 = 0;
    puVar18[1] = uVar16;
    *puVar18 = local_c0;
    local_c0 = 0;
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar18,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEEE_03bd69c0,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEED2Ev_03bd2250);
  }
  lVar13 = _ZN5Sfs2X4Util9ByteArray6LengthEv(local_78);
  uVar10 = _ZN5Sfs2X8Bitswarm14BitSwarmClient10UseBlueBoxEv(*(undefined8 *)(param_1 + 0x28));
  uVar16 = _Znwm(0x10);
                    /* try { // try from 02b44268 to 02c44297 has its CatchHandler @ 02b454d0 */
  _ZN5Sfs2X4Core12PacketHeaderC2Ebbbb(uVar16,uVar8 & 1,lVar12 < lVar11,uVar10 & 1,0xffff < lVar13);
  local_d8 = (long *)0x0;
  local_e0 = uVar16;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_e0,uVar16,&local_d8);
  uVar19 = _ZN5Sfs2X8Bitswarm14BitSwarmClient5DebugEv(*(undefined8 *)(param_1 + 0x28));
  if ((uVar19 & 1) != 0) {
    puVar18 = (undefined8 *)_Znwm(0x18);
    puVar18[1] = 0;
    puVar18[2] = 0;
    *puVar18 = 0;
                    /* try { // try from 02b442c0 to 02c442ef has its CatchHandler @ 02b454cc */
    _ZN5boost10shared_ptrISt6vectorISsSaISsEEEC2IS3_EEPT_(&local_f0,puVar18);
    plVar15 = (long *)_Znwm(8);
    *plVar15 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_100,plVar15);
    uVar16 = _Znwm(8);
    FUN_0307a6fc(uVar16,"Data written: %s",&local_98);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_110,uVar16);
    plVar3 = local_f8;
    plVar2 = local_100;
    plVar15 = local_108;
    if (local_f8 != (long *)0x0) {
      plVar4 = local_f8 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar4,0x10);
        if (bVar6) {
          *(int *)plVar4 = (int)*plVar4 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    if (local_108 != (long *)0x0) {
      plVar4 = local_108 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar4,0x10);
        if (bVar6) {
          *(int *)plVar4 = (int)*plVar4 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
                    /* try { // try from 02b44358 to 02c4435f has its CatchHandler @ 02b45684 */
    (**(code **)(*(long *)*param_2 + 0x10))(&local_130);
    (**(code **)(*local_130 + 0x58))(&local_120);
    lVar11 = *(long *)(*plVar2 + -0x18);
                    /* try { // try from 02b44388 to 02c44397 has its CatchHandler @ 02b4561c */
    uVar16 = *local_120;
    FUN_0307d194(plVar2,lVar11 + 0x1000,0);
    iVar9 = sprintf((char *)*plVar2,(char *)*local_110,uVar16);
    if (iVar9 < 0) {
                    /* try { // try from 02b4455c to 02c4458f has its CatchHandler @ 02b4534c */
      FUN_0307d194(plVar2,lVar11,0);
    }
    else {
      FUN_0307d194(plVar2,lVar11 + iVar9,0);
    }
                    /* try { // try from 02b443c0 to 02c443ef has its CatchHandler @ 02b454dc */
    if (local_118 != (long *)0x0) {
      plVar2 = local_118 + 1;
      do {
        iVar9 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_118 + 0x10))(local_118);
        piVar1 = (int *)((long)local_118 + 0xc);
        do {
          iVar9 = *piVar1;
                    /* try { // try from 02b443f8 to 02c44417 has its CatchHandler @ 02b44e94 */
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_118 + 0x18))(local_118);
        }
      }
    }
                    /* try { // try from 02b44418 to 02c44423 has its CatchHandler @ 02b44d00 */
    if (local_128 != (long *)0x0) {
      plVar2 = local_128 + 1;
      do {
                    /* try { // try from 02b44424 to 02c44437 has its CatchHandler @ 02b44ce4 */
        iVar9 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b44438 to 02c44443 has its CatchHandler @ 02b44ce0 */
        (**(code **)(*local_128 + 0x10))(local_128);
        piVar1 = (int *)((long)local_128 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_128 + 0x18))(local_128);
        }
      }
    }
    if (plVar15 != (long *)0x0) {
      plVar2 = plVar15 + 1;
      do {
        iVar9 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b4448c to 02c444bb has its CatchHandler @ 02b44d18 */
        (**(code **)(*plVar15 + 0x10))(plVar15);
        piVar1 = (int *)((long)plVar15 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
                    /* try { // try from 02b444c0 to 02c444e7 has its CatchHandler @ 02b454bc */
          (**(code **)(*plVar15 + 0x18))(plVar15);
        }
      }
    }
    if (plVar3 != (long *)0x0) {
      plVar15 = plVar3 + 1;
      do {
        iVar9 = (int)*plVar15 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b444e8 to 02c444f3 has its CatchHandler @ 02b45334 */
        (**(code **)(*plVar3 + 0x10))(plVar3);
        piVar1 = (int *)((long)plVar3 + 0xc);
        do {
                    /* try { // try from 02b444f4 to 02c44507 has its CatchHandler @ 02b4531c */
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
                    /* try { // try from 02b44508 to 02c44513 has its CatchHandler @ 02b45318 */
          (**(code **)(*plVar3 + 0x18))(plVar3);
        }
      }
    }
    lVar11 = local_f0;
    if (*(long *)(local_f0 + 8) == *(long *)(local_f0 + 0x10)) {
      _ZNSt6vectorISsSaISsEE19_M_emplace_back_auxIJRKSsEEEvDpOT_(local_f0,local_100);
    }
    else {
      FUN_0307e06c();
      *(long *)(lVar11 + 8) = *(long *)(lVar11 + 8) + 8;
    }
    uVar16 = *(undefined8 *)(param_1 + 0x38);
    local_140 = local_f0;
    local_138 = local_e8;
    if (local_e8 != (long *)0x0) {
      plVar15 = local_e8 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = (int)*plVar15 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    _ZN5Sfs2X7Logging6Logger4InfoEN5boost10shared_ptrISt6vectorISsSaISsEEEE(uVar16,&local_140);
    plVar15 = local_138;
    if (local_138 != (long *)0x0) {
      plVar2 = local_138 + 1;
      do {
        iVar9 = (int)*plVar2 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar6) {
          *(int *)plVar2 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b445b4 to 02c445e3 has its CatchHandler @ 02b45038 */
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_138 + 0x10))(local_138);
        piVar1 = (int *)((long)plVar15 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar15 + 0x18))(plVar15);
        }
      }
    }
    if (local_108 != (long *)0x0) {
      plVar15 = local_108 + 1;
      do {
        iVar9 = (int)*plVar15 + -1;
                    /* try { // try from 02b44608 to 02c44637 has its CatchHandler @ 02b45034 */
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_108 + 0x10))(local_108);
        piVar1 = (int *)((long)local_108 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
                    /* try { // try from 02b44638 to 02c44643 has its CatchHandler @ 02b45308 */
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_108 + 0x18))(local_108);
        }
      }
    }
    if (local_f8 != (long *)0x0) {
      plVar15 = local_f8 + 1;
      do {
        iVar9 = (int)*plVar15 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b44664 to 02c4466f has its CatchHandler @ 02b4528c */
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_f8 + 0x10))(local_f8);
                    /* try { // try from 02b4467c to 02c44687 has its CatchHandler @ 02b45214 */
        piVar1 = (int *)((long)local_f8 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_f8 + 0x18))(local_f8);
        }
      }
    }
    if (local_e8 != (long *)0x0) {
      plVar15 = local_e8 + 1;
      do {
                    /* try { // try from 02b446b0 to 02c446df has its CatchHandler @ 02b45344 */
        iVar9 = (int)*plVar15 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
        if (bVar6) {
          *(int *)plVar15 = iVar9;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_e8 + 0x10))(local_e8);
        piVar1 = (int *)((long)local_e8 + 0xc);
        do {
          iVar9 = *piVar1;
                    /* try { // try from 02b446e0 to 02c446fb has its CatchHandler @ 02b44088 */
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar9 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_e8 + 0x18))(local_e8);
        }
      }
    }
  }
                    /* try { // try from 02b446fc to 02c4470f has its CatchHandler @ 02b451b0 */
  local_150 = (undefined8 *)_Znwm(0x10);
                    /* try { // try from 02b44714 to 02c4473b has its CatchHandler @ 02b45348 */
  local_148 = (long *)0x0;
  *local_150 = 
  PTR__ZN5Sfs2X4Core12SFSIOHandler15WriteBinaryDataEyN5boost10shared_ptrINS0_12PacketHeaderEEENS3_INS_4Util9ByteArrayEEEb_03bcf070
  ;
  local_150[1] = param_1;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE
            (&local_150,local_150,&local_148);
  local_160 = (byte *)_Znwm(1);
                    /* try { // try from 02b4473c to 02c44747 has its CatchHandler @ 02b45024 */
  *local_160 = 0;
  local_158 = (long *)0x0;
                    /* try { // try from 02b44748 to 02c4475b has its CatchHandler @ 02b4500c */
  _ZN5boost6detail20sp_pointer_constructIbbEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_160,local_160,&local_158);
                    /* try { // try from 02b4475c to 02c44767 has its CatchHandler @ 02b45008 */
  bVar7 = (**(code **)(*(long *)*param_2 + 0x40))();
  *local_160 = bVar7 & 1;
  _ZN5Sfs2X8Bitswarm14BitSwarmClient13ThreadManagerEv(&local_170,*(undefined8 *)(param_1 + 0x28));
  local_180 = local_150;
  local_178 = local_148;
  if (local_148 != (long *)0x0) {
    plVar15 = local_148 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = (int)*plVar15 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  local_190 = local_e0;
  local_188 = local_d8;
  if (local_d8 != (long *)0x0) {
    plVar15 = local_d8 + 1;
    do {
                    /* try { // try from 02b447b0 to 02c447df has its CatchHandler @ 02b45040 */
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = (int)*plVar15 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  local_1a0 = local_78;
  local_198 = local_70;
  if (local_70 != (long *)0x0) {
    plVar15 = local_70 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = (int)*plVar15 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  local_1b0 = local_160;
  local_1a8 = local_158;
  if (local_158 != (long *)0x0) {
    plVar15 = local_158 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = (int)*plVar15 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b44804 to 02c44833 has its CatchHandler @ 02b44e9c */
    } while (cVar5 != '\0');
  }
  _ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE
            (local_170,&local_180,&local_190,&local_1a0,&local_1b0);
  plVar15 = local_1a8;
  if (local_1a8 != (long *)0x0) {
    plVar2 = local_1a8 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_1a8 + 0x10))(local_1a8);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
                    /* try { // try from 02b44858 to 02c44887 has its CatchHandler @ 02b44e98 */
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  plVar15 = local_198;
  if (local_198 != (long *)0x0) {
    plVar2 = local_198 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
                    /* try { // try from 02b44888 to 02c44893 has its CatchHandler @ 02b44ff8 */
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_198 + 0x10))(local_198);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b448b4 to 02c448bf has its CatchHandler @ 02b44f7c */
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
                    /* try { // try from 02b448cc to 02c448d7 has its CatchHandler @ 02b44f04 */
  plVar15 = local_188;
  if (local_188 != (long *)0x0) {
    plVar2 = local_188 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_188 + 0x10))(local_188);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
                    /* try { // try from 02b44900 to 02c4492f has its CatchHandler @ 02b4503c */
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  plVar15 = local_178;
  if (local_178 != (long *)0x0) {
    plVar2 = local_178 + 1;
    do {
                    /* try { // try from 02b44930 to 02c4494b has its CatchHandler @ 02b44088 */
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b4494c to 02c4495f has its CatchHandler @ 02b44ea0 */
      (**(code **)(*local_178 + 0x10))(local_178);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b44964 to 02c44973 has its CatchHandler @ 02b4534c */
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  if (local_168 != (long *)0x0) {
    plVar15 = local_168 + 1;
    do {
      iVar9 = (int)*plVar15 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_168 + 0x10))(local_168);
      piVar1 = (int *)((long)local_168 + 0xc);
      do {
        iVar9 = *piVar1;
                    /* try { // try from 02b449b4 to 02c449c3 has its CatchHandler @ 02b45040 */
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b449c8 to 02c449d7 has its CatchHandler @ 02b44d18 */
        (**(code **)(*local_168 + 0x18))(local_168);
      }
    }
  }
  plVar15 = local_158;
  if (local_158 != (long *)0x0) {
    plVar2 = local_158 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b449fc to 02c44a2b has its CatchHandler @ 02b44b64 */
      (**(code **)(*local_158 + 0x10))(local_158);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  plVar15 = local_148;
  if (local_148 != (long *)0x0) {
    plVar2 = local_148 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b44a50 to 02c44a7f has its CatchHandler @ 02b44b60 */
      (**(code **)(*local_148 + 0x10))(local_148);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b44a80 to 02c44a8b has its CatchHandler @ 02b44ccc */
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  plVar15 = local_d8;
  if (local_d8 != (long *)0x0) {
    plVar2 = local_d8 + 1;
    do {
      iVar9 = (int)*plVar2 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar6) {
        *(int *)plVar2 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b44aac to 02c44ab7 has its CatchHandler @ 02b44c4c */
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar1 = (int *)((long)plVar15 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b44ac4 to 02c44acf has its CatchHandler @ 02b44bd0 */
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar15 + 0x18))(plVar15);
      }
    }
  }
  if (local_70 != (long *)0x0) {
    plVar15 = local_70 + 1;
    do {
      iVar9 = (int)*plVar15 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar15,0x10);
      if (bVar6) {
        *(int *)plVar15 = iVar9;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
                    /* try { // try from 02b44af8 to 02c44b27 has its CatchHandler @ 02b44d14 */
    if (iVar9 == 0) {
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar1 = (int *)((long)local_70 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar9 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b44b28 to 02c44b43 has its CatchHandler @ 02b44088 */
        (**(code **)(*local_70 + 0x18))(local_70);
      }
    }
  }
  if (*(long *)(lVar20 + 0x28) == local_68) {
                    /* try { // try from 02b44b44 to 02c44b57 has its CatchHandler @ 02b44b68 */
                    /* try { // try from 02b44b58 to 02c44b97 has its CatchHandler @ 02b44088 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b44a50 with catch @ 02b44b60
                        */
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02b449fc with catch @ 02b44b64
                        */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02b457ac
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Protocol14IProtocolCodecENS2_4Core16SFSProtocolCodecEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
                    /* try { // try from 02b457cc to 02c457e3 has its CatchHandler @ 02b458a0 */
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEEE_03bdaf38;
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
                    /* try { // try from 02b4584c to 02c4587b has its CatchHandler @ 02b45920 */
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,param_2,param_2);
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEED0Ev
// ADDRESS : 02b45894
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEED0Ev(void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE7disposeEv
// ADDRESS : 02b45898
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE7disposeEv(long param_1)

{
  if (*(long **)(param_1 + 0x10) != (long *)0x0) {
                    /* catch() { ... } // from try @ 02b457cc with catch @ 02b458a0 */
                    /* WARNING: Could not recover jumptable at 0x02b458a8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(**(long **)(param_1 + 0x10) + 0x30))();
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE11get_deleterERKSt9type_info
// ADDRESS : 02b458b0
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE11get_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE17get_local_deleterERKSt9type_info
// ADDRESS : 02b458b8
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE19get_untyped_deleterEv
// ADDRESS : 02b458c0
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core16SFSProtocolCodecEE19get_untyped_deleterEv(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02b45a60
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEEE_03bd0be8;
                    /* try { // try from 02b45a90 to 02c45abf has its CatchHandler @ 02b479cc */
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
                    /* try { // try from 02b45ac8 to 02c45adb has its CatchHandler @ 02b487e4 */
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
                    /* try { // try from 02b45afc to 02c45b0b has its CatchHandler @ 02b47cec */
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,param_2,param_2);
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEED0Ev
// ADDRESS : 02b45b40
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEED0Ev(void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE7disposeEv
// ADDRESS : 02b45b44
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE7disposeEv(long param_1)

{
  if (*(void **)(param_1 + 0x10) != (void *)0x0) {
    _ZdlPv(*(void **)(param_1 + 0x10));
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE11get_deleterERKSt9type_info
// ADDRESS : 02b45b54
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE11get_deleterERKSt9type_info(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE17get_local_deleterERKSt9type_info
// ADDRESS : 02b45b5c
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE19get_untyped_deleterEv
// ADDRESS : 02b45b64
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Core12PacketHeaderEE19get_untyped_deleterEv(void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE
// ADDRESS : 02b45b6c
================================================================

void _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEESB_EEvPNS5_IT_EEPT0_RNS0_12shared_countE
               (undefined8 param_1,long param_2,undefined8 *param_3)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  undefined *puVar5;
  long *plVar6;
  long *plVar7;
  
  plVar6 = (long *)_Znwm(0x18);
  puVar5 = 
  PTR__ZTVN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEEE_03bd1cb8
  ;
  plVar6[2] = param_2;
  *plVar6 = (long)(puVar5 + 0x10);
  plVar6[1] = 0x100000001;
  plVar7 = (long *)*param_3;
                    /* try { // try from 02b45bac to 02c45bb7 has its CatchHandler @ 02b47c44 */
  *param_3 = plVar6;
  if (plVar7 != (long *)0x0) {
    plVar6 = plVar7 + 1;
    do {
      iVar4 = (int)*plVar6 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar6,0x10);
      if (bVar3) {
        *(int *)plVar6 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*plVar7 + 0x10))(plVar7);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b45bec to 02c45bfb has its CatchHandler @ 02b47a60 */
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,param_2,param_2);
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEED0Ev
// ADDRESS : 02b45c4c
================================================================

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEED0Ev
               (void *__ptr)

{
  (*(code *)PTR__ZdlPv_03bc54a8)();
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE7disposeEv
// ADDRESS : 02b45c50
================================================================

void _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE7disposeEv
               (long param_1)

{
  if (*(void **)(param_1 + 0x10) != (void *)0x0) {
    _ZdlPv(*(void **)(param_1 + 0x10));
    return;
  }
  return;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE11get_deleterERKSt9type_info
// ADDRESS : 02b45c60
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE11get_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE17get_local_deleterERKSt9type_info
// ADDRESS : 02b45c68
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE17get_local_deleterERKSt9type_info
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE19get_untyped_deleterEv
// ADDRESS : 02b45c70
================================================================

undefined8
_ZN5boost6detail17sp_counted_impl_pIN5Sfs2X4Util22DelegateThreeArgumentsINS_10shared_ptrINS2_4Core12PacketHeaderEEENS5_INS3_9ByteArrayEEEbEEE19get_untyped_deleterEv
          (void)

{
  return 0;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
// ADDRESS : 02b45c78
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodecC1EN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEENS3_INS4_14BitSwarmClientEEE
               (long *param_1,long *param_2,long *param_3)

{
  int *piVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  long *plVar8;
  long *plVar9;
  long local_48;
  long *local_40;
  long local_38;
  
                    /* try { // try from 02b45c78 to 02c45c87 has its CatchHandler @ 02b4834c */
  lVar7 = tpidr_el0;
  local_38 = *(long *)(lVar7 + 0x28);
  *param_1 = (long)(PTR__ZTVN5Sfs2X4Core16SFSProtocolCodecE_03bd8b58 + 0x10);
  param_1[6] = 0;
  param_1[5] = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
                    /* try { // try from 02b45cbc to 02c45ceb has its CatchHandler @ 02b47a58 */
  lVar2 = *param_2;
  lVar3 = param_2[1];
  if (lVar3 == 0) {
    param_1[1] = lVar2;
    param_1[2] = 0;
  }
  else {
    piVar1 = (int *)(lVar3 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar5) {
        *piVar1 = *piVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    plVar8 = (long *)param_1[2];
    param_1[1] = lVar2;
    param_1[2] = lVar3;
    if (plVar8 != (long *)0x0) {
      plVar9 = plVar8 + 1;
      do {
        iVar6 = (int)*plVar9 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar5) {
          *(int *)plVar9 = iVar6;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 == 0) {
        (**(code **)(*plVar8 + 0x10))(plVar8);
        piVar1 = (int *)((long)plVar8 + 0xc);
        do {
                    /* try { // try from 02b45d14 to 02c45d43 has its CatchHandler @ 02b47a10 */
          iVar6 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar6 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar6 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
        }
      }
    }
  }
  _ZN5Sfs2X8Bitswarm14BitSwarmClient3LogEv(&local_48,*param_3);
  plVar8 = local_40;
  lVar2 = local_48;
  local_48 = 0;
  local_40 = (long *)0x0;
  plVar9 = (long *)param_1[4];
  param_1[3] = lVar2;
  param_1[4] = (long)plVar8;
  if (plVar9 != (long *)0x0) {
    plVar8 = plVar9 + 1;
    do {
      iVar6 = (int)*plVar8 + -1;
                    /* try { // try from 02b45d6c to 02c45d9b has its CatchHandler @ 02b479c8 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar5) {
        *(int *)plVar8 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar8 = local_40;
  if (local_40 != (long *)0x0) {
    plVar9 = local_40 + 1;
    do {
                    /* try { // try from 02b45dc0 to 02c45dcb has its CatchHandler @ 02b482ec */
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b45e00 to 02c45e2f has its CatchHandler @ 02b47a54 */
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  lVar2 = *param_3;
  lVar3 = param_3[1];
  if (lVar3 != 0) {
    piVar1 = (int *)(lVar3 + 8);
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar5) {
        *piVar1 = *piVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  plVar8 = (long *)param_1[6];
  param_1[5] = lVar2;
  param_1[6] = lVar3;
  if (plVar8 != (long *)0x0) {
    plVar9 = plVar8 + 1;
    do {
      iVar6 = (int)*plVar9 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar5) {
        *(int *)plVar9 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar8 + 0x10))(plVar8);
                    /* try { // try from 02b45e58 to 02c45e87 has its CatchHandler @ 02b47a0c */
      piVar1 = (int *)((long)plVar8 + 0xc);
      do {
        iVar6 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec7DisposeEv
// ADDRESS : 02b45fd8
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec7DisposeEv(long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = *(long **)(param_1 + 0x10);
  *(undefined8 *)(param_1 + 8) = 0;
  *(undefined8 *)(param_1 + 0x10) = 0;
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
                    /* try { // try from 02b45ff8 to 02c46027 has its CatchHandler @ 02b479c0 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = *(long **)(param_1 + 0x20);
  *(undefined8 *)(param_1 + 0x18) = 0;
  *(undefined8 *)(param_1 + 0x20) = 0;
                    /* try { // try from 02b4604c to 02c46057 has its CatchHandler @ 02b4822c */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b4608c to 02c460bb has its CatchHandler @ 02b47a4c */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = *(long **)(param_1 + 0x30);
  *(undefined8 *)(param_1 + 0x28) = 0;
  *(undefined8 *)(param_1 + 0x30) = 0;
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b460e4 to 02c46113 has its CatchHandler @ 02b47a04 */
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodecD2Ev
// ADDRESS : 02b46114
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodecD2Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[6];
  *param_1 = (long)(PTR__ZTVN5Sfs2X4Core16SFSProtocolCodecE_03bd8b58 + 0x10);
  if (plVar6 != (long *)0x0) {
                    /* try { // try from 02b4613c to 02c4616b has its CatchHandler @ 02b479bc */
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[4];
                    /* try { // try from 02b46190 to 02c4619b has its CatchHandler @ 02b481cc */
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b461d0 to 02c461ff has its CatchHandler @ 02b47a48 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  plVar6 = (long *)param_1[2];
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
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
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
                    /* try { // try from 02b46228 to 02c46257 has its CatchHandler @ 02b47a00 */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodecD0Ev
// ADDRESS : 02b46254
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodecD0Ev(void *param_1)

{
  _ZN5Sfs2X4Core16SFSProtocolCodecD2Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec9IOHandlerEv
// ADDRESS : 02b46278
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec9IOHandlerEv(undefined8 *param_1,long param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  
  *param_1 = *(undefined8 *)(param_2 + 8);
                    /* try { // try from 02b46280 to 02c462af has its CatchHandler @ 02b479b8 */
  lVar4 = *(long *)(param_2 + 0x10);
  param_1[1] = lVar4;
  if (lVar4 != 0) {
    piVar1 = (int *)(lVar4 + 8);
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar3) {
        *piVar1 = *piVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec9IOHandlerEN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEE
// ADDRESS : 02b462a4
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec9IOHandlerEN5boost10shared_ptrINS_8Bitswarm9IoHandlerEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  long *plVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  long *plVar8;
  undefined8 uVar9;
  undefined8 *puVar10;
  long lVar11;
  long *local_90;
  long *local_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 *local_68;
  long *plStack_60;
  long *local_58;
  long *plStack_50;
  long local_48;
  
  lVar11 = tpidr_el0;
  local_48 = *(long *)(lVar11 + 0x28);
  if (*(long *)(param_1 + 8) != 0) {
                    /* try { // try from 02b462d4 to 02c462df has its CatchHandler @ 02b4816c */
    plVar8 = (long *)_Znwm(8);
    *plVar8 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_58,plVar8);
    uVar9 = _Znwm(8);
                    /* try { // try from 02b46314 to 02c46343 has its CatchHandler @ 02b47a44 */
    FUN_0307a6fc(uVar9,"IOHandler is already defined for thir ProtocolHandler instance: 0x%x",
                 &local_80);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar9);
    plVar3 = plStack_50;
    plVar8 = local_58;
    if (plStack_50 != (long *)0x0) {
      plVar1 = plStack_50 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar6) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    if (plStack_60 != (long *)0x0) {
      plVar1 = plStack_60 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar6) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    lVar11 = *(long *)(*local_58 + -0x18);
                    /* try { // try from 02b4636c to 02c4639b has its CatchHandler @ 02b479fc */
    FUN_0307d194(local_58,lVar11 + 0x1000,0);
    iVar7 = sprintf((char *)*plVar8,(char *)*local_68,param_1);
    if (iVar7 < 0) {
      FUN_0307d194(plVar8,lVar11,0);
    }
    else {
      FUN_0307d194(plVar8,lVar11 + iVar7,0);
    }
    if (plStack_60 != (long *)0x0) {
      plVar8 = plStack_60 + 1;
      do {
        iVar7 = (int)*plVar8 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar8,0x10);
        if (bVar6) {
          *(int *)plVar8 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
                    /* try { // try from 02b463c4 to 02c463f3 has its CatchHandler @ 02b479b4 */
        (**(code **)(*plStack_60 + 0x10))(plStack_60);
        piVar2 = (int *)((long)plStack_60 + 0xc);
        do {
          iVar7 = *piVar2;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar6) {
            *piVar2 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plStack_60 + 0x18))(plStack_60);
        }
      }
    }
    if (plVar3 != (long *)0x0) {
      plVar8 = plVar3 + 1;
      do {
        iVar7 = (int)*plVar8 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar8,0x10);
        if (bVar6) {
          *(int *)plVar8 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
                    /* try { // try from 02b46418 to 02c46427 has its CatchHandler @ 02b4810c */
        (**(code **)(*plVar3 + 0x10))(plVar3);
        piVar2 = (int *)((long)plVar3 + 0xc);
        do {
          iVar7 = *piVar2;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar6) {
            *piVar2 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar3 + 0x18))(plVar3);
        }
      }
    }
    local_80 = _Znwm(0x38);
    local_90 = local_58;
    local_88 = plStack_50;
    if (plStack_50 != (long *)0x0) {
                    /* try { // try from 02b4645c to 02c4648b has its CatchHandler @ 02b47a40 */
      plStack_50 = plStack_50 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plStack_50,0x10);
        if (bVar6) {
          *(int *)plStack_50 = (int)*plStack_50 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    _ZN5Sfs2X10Exceptions13SFSCodecErrorC1EN5boost10shared_ptrISsEE(local_80,&local_90);
    uStack_78 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions13SFSCodecErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_80,local_80,(ulong)&local_80 | 8);
    plVar8 = local_88;
    if (local_88 != (long *)0x0) {
      plVar3 = local_88 + 1;
      do {
        iVar7 = (int)*plVar3 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar3,0x10);
        if (bVar6) {
          *(int *)plVar3 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
                    /* try { // try from 02b464b4 to 02c464e3 has its CatchHandler @ 02b479f8 */
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar2 = (int *)((long)plVar8 + 0xc);
        do {
          iVar7 = *piVar2;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar6) {
            *piVar2 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
        }
      }
    }
    puVar10 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar9 = uStack_78;
    puVar10[1] = 0;
    uStack_78 = 0;
    puVar10[1] = uVar9;
    *puVar10 = local_80;
    local_80 = 0;
                    /* try { // try from 02b4650c to 02c4653b has its CatchHandler @ 02b479b0 */
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar10,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEEE_03bd69c0,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEED2Ev_03bd2250);
  }
  uVar9 = *param_2;
  lVar4 = param_2[1];
  if (lVar4 != 0) {
    piVar2 = (int *)(lVar4 + 8);
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(piVar2,0x10);
      if (bVar6) {
        *piVar2 = *piVar2 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  plVar8 = *(long **)(param_1 + 0x10);
  *(undefined8 *)(param_1 + 8) = uVar9;
  *(long *)(param_1 + 0x10) = lVar4;
                    /* try { // try from 02b46540 to 02c46567 has its CatchHandler @ 02b487e4 */
  if (plVar8 != (long *)0x0) {
    plVar3 = plVar8 + 1;
    do {
      iVar7 = (int)*plVar3 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar6) {
        *(int *)plVar3 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02b46568 to 02c46573 has its CatchHandler @ 02b47cdc */
      (**(code **)(*plVar8 + 0x10))(plVar8);
      piVar2 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar2;
                    /* try { // try from 02b46574 to 02c46587 has its CatchHandler @ 02b47cc0 */
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar6) {
          *piVar2 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02b46588 to 02c46593 has its CatchHandler @ 02b47c40 */
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if (*(long *)(lVar11 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec12OnPacketReadEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 02b468f0
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec12OnPacketReadEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (undefined8 param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 local_38;
  long *plStack_30;
  long local_28;
  
  lVar7 = tpidr_el0;
  local_28 = *(long *)(lVar7 + 0x28);
  local_38 = *param_2;
  plVar3 = (long *)param_2[1];
  if (plVar3 != (long *)0x0) {
    plVar1 = plVar3 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b4692c to 02c4695b has its CatchHandler @ 02b47a38 */
  plStack_30 = plVar3;
  _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,&local_38);
  if (plVar3 != (long *)0x0) {
    plVar1 = plVar3 + 1;
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
      (**(code **)(*plVar3 + 0x10))(plVar3);
      piVar2 = (int *)((long)plVar3 + 0xc);
      do {
        iVar6 = *piVar2;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar5) {
          *piVar2 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
                    /* try { // try from 02b46984 to 02c469b3 has its CatchHandler @ 02b479f0 */
        (**(code **)(*plVar3 + 0x18))(plVar3);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_28) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
// ADDRESS : 02b46a14
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  long *plVar2;
  byte bVar3;
  char cVar4;
  bool bVar5;
  undefined *puVar6;
  undefined *puVar7;
  uint uVar8;
  int iVar9;
  long *plVar10;
  ulong uVar11;
  undefined8 uVar12;
  undefined8 *puVar13;
  long *plVar14;
  code *pcVar15;
  code *pcVar16;
  long lVar17;
  long *local_1e0;
  long *local_1d8;
  long *local_1d0;
  long *local_1c8;
  undefined8 local_1c0;
  undefined8 uStack_1b8;
  undefined8 *local_1b0;
  long *plStack_1a8;
  long *local_1a0;
  long *plStack_198;
  long *local_190;
  long *local_188;
  undefined8 local_180;
  long *local_178;
  byte *local_170;
  long *plStack_168;
  undefined8 local_160;
  long *local_158;
  undefined8 *local_150;
  long *local_148;
  undefined8 local_140;
  long *local_138;
  undefined8 local_130;
  long *local_128;
  undefined1 auStack_120 [8];
  long *local_118;
  undefined8 local_110;
  long *local_108;
  short *local_100;
  long *local_f8;
  undefined8 local_f0;
  long *local_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 local_d0;
  long *plStack_c8;
  undefined8 local_c0;
  long *local_b8;
  undefined8 local_b0;
  long *local_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 local_88;
  long *plStack_80;
  undefined8 local_78;
  long *local_70;
  long *local_68;
  long *local_60;
  long local_58;
  
                    /* try { // try from 02b46a30 to 02c46a3b has its CatchHandler @ 02b47fec */
  lVar17 = tpidr_el0;
  local_58 = *(long *)(lVar17 + 0x28);
  plVar10 = (long *)_Znwm(0x38);
  _ZN5Sfs2X8Bitswarm7MessageC2Ev();
  local_60 = (long *)0x0;
  local_68 = plVar10;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Bitswarm8IMessageENS3_7MessageEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_68,plVar10,&local_60);
  puVar7 = PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278;
  plVar10 = (long *)*param_2;
                    /* try { // try from 02b46a70 to 02c46a9f has its CatchHandler @ 02b47a34 */
  pcVar15 = *(code **)(*plVar10 + 8);
  local_78 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278;
  local_70 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278 + 8);
  if (local_70 != (long *)0x0) {
    plVar14 = local_70 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = (int)*plVar14 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  uVar11 = (*pcVar15)(plVar10,&local_78);
  plVar10 = local_70;
  if (local_70 != (long *)0x0) {
    plVar14 = local_70 + 1;
    do {
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b46ac8 to 02c46af7 has its CatchHandler @ 02b479ec */
    if (iVar9 == 0) {
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  puVar6 = PTR__ZN5Sfs2X4Core16SFSProtocolCodec9ACTION_IDE_03bcfef0;
  if ((uVar11 & 1) != 0) {
    uVar12 = _Znwm(8);
                    /* try { // try from 02b46b20 to 02c46b4f has its CatchHandler @ 02b479a4 */
    FUN_0307a6fc(uVar12,"Request rejected: No Controller ID in request!",&local_a0);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_88,uVar12);
    local_a0 = _Znwm(0x38);
    local_b0 = local_88;
    local_a8 = plStack_80;
    if (plStack_80 != (long *)0x0) {
      plStack_80 = plStack_80 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plStack_80,0x10);
        if (bVar5) {
          *(int *)plStack_80 = (int)*plStack_80 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    _ZN5Sfs2X10Exceptions13SFSCodecErrorC1EN5boost10shared_ptrISsEE(local_a0,&local_b0);
                    /* try { // try from 02b46b74 to 02c46b83 has its CatchHandler @ 02b47f8c */
    uStack_98 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions13SFSCodecErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_a0,local_a0,(ulong)&local_a0 | 8);
    plVar10 = local_a8;
    if (local_a8 != (long *)0x0) {
      plVar14 = local_a8 + 1;
      do {
        iVar9 = (int)*plVar14 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar5) {
          *(int *)plVar14 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b46bb8 to 02c46be7 has its CatchHandler @ 02b47a30 */
        (**(code **)(*local_a8 + 0x10))(local_a8);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    puVar13 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar12 = uStack_98;
    puVar13[1] = 0;
    uStack_98 = 0;
    puVar13[1] = uVar12;
    *puVar13 = local_a0;
    local_a0 = 0;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 02b46c10 to 02c46c3f has its CatchHandler @ 02b479e8 */
    __cxa_throw(puVar13,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEEE_03bd69c0,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEED2Ev_03bd2250);
  }
  plVar10 = (long *)*param_2;
  pcVar15 = *(code **)(*plVar10 + 8);
  local_c0 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec9ACTION_IDE_03bcfef0;
  local_b8 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec9ACTION_IDE_03bcfef0 + 8);
  if (local_b8 != (long *)0x0) {
    plVar14 = local_b8 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = (int)*plVar14 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  uVar11 = (*pcVar15)(plVar10,&local_c0);
  plVar10 = local_b8;
  if (local_b8 != (long *)0x0) {
    plVar14 = local_b8 + 1;
    do {
                    /* try { // try from 02b46c68 to 02c46c97 has its CatchHandler @ 02b479a0 */
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_b8 + 0x10))(local_b8);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_68;
  if ((uVar11 & 1) != 0) {
    uVar12 = _Znwm(8);
                    /* try { // try from 02b46cbc to 02c46ccb has its CatchHandler @ 02b47f2c */
    FUN_0307a6fc(uVar12,"Request rejected: No Action ID in request!",&local_88);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_d0,uVar12);
    local_e0 = _Znwm(0x38);
    local_f0 = local_d0;
    local_e8 = plStack_c8;
    if (plStack_c8 != (long *)0x0) {
                    /* try { // try from 02b46d00 to 02c46d2f has its CatchHandler @ 02b47a2c */
      plStack_c8 = plStack_c8 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plStack_c8,0x10);
        if (bVar5) {
          *(int *)plStack_c8 = (int)*plStack_c8 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    _ZN5Sfs2X10Exceptions13SFSCodecErrorC1EN5boost10shared_ptrISsEE(local_e0,&local_f0);
    uStack_d8 = 0;
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions13SFSCodecErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_e0,local_e0,(ulong)&local_e0 | 8);
    plVar10 = local_e8;
    if (local_e8 != (long *)0x0) {
      plVar14 = local_e8 + 1;
      do {
        iVar9 = (int)*plVar14 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar5) {
          *(int *)plVar14 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b46d58 to 02c46d87 has its CatchHandler @ 02b479e4 */
        (**(code **)(*local_e8 + 0x10))(local_e8);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    puVar13 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar12 = uStack_d8;
    puVar13[1] = 0;
    uStack_d8 = 0;
    puVar13[1] = uVar12;
    *puVar13 = local_e0;
    local_e0 = 0;
                    /* try { // try from 02b46db0 to 02c46ddf has its CatchHandler @ 02b4799c */
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar13,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEEE_03bd69c0,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEED2Ev_03bd2250);
  }
  plVar14 = (long *)*param_2;
  local_110 = *(undefined8 *)puVar6;
  local_108 = *(long **)(puVar6 + 8);
  pcVar16 = *(code **)(*local_68 + 8);
  pcVar15 = *(code **)(*plVar14 + 0x98);
  if (local_108 != (long *)0x0) {
    plVar2 = local_108 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b46e04 to 02c46e0f has its CatchHandler @ 02b47ecc */
  (*pcVar15)(&local_100,plVar14,&local_110);
  (*pcVar16)(plVar10,(long)*local_100);
  if (local_f8 != (long *)0x0) {
    plVar10 = local_f8 + 1;
    do {
      iVar9 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b46e44 to 02c46e73 has its CatchHandler @ 02b47a28 */
      (**(code **)(*local_f8 + 0x10))(local_f8);
      piVar1 = (int *)((long)local_f8 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_f8 + 0x18))(local_f8);
      }
    }
  }
  plVar10 = local_108;
  if (local_108 != (long *)0x0) {
    plVar14 = local_108 + 1;
    do {
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b46e9c to 02c46ecb has its CatchHandler @ 02b479e0 */
      (**(code **)(*local_108 + 0x10))(local_108);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_68;
  plVar14 = (long *)*param_2;
  local_130 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8;
  local_128 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8 + 8);
  pcVar16 = *(code **)(*local_68 + 0x18);
  pcVar15 = *(code **)(*plVar14 + 0x198);
  if (local_128 != (long *)0x0) {
                    /* try { // try from 02b46ef4 to 02c46f23 has its CatchHandler @ 02b47998 */
    plVar2 = local_128 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  (*pcVar15)(auStack_120,plVar14,&local_130);
  (*pcVar16)(plVar10,auStack_120);
  if (local_118 != (long *)0x0) {
    plVar10 = local_118 + 1;
    do {
      iVar9 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
                    /* try { // try from 02b46f48 to 02c46f53 has its CatchHandler @ 02b47e6c */
      (**(code **)(*local_118 + 0x10))(local_118);
      piVar1 = (int *)((long)local_118 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_118 + 0x18))(local_118);
      }
    }
  }
  plVar10 = local_128;
  if (local_128 != (long *)0x0) {
    plVar14 = local_128 + 1;
    do {
                    /* try { // try from 02b46f88 to 02c46fb7 has its CatchHandler @ 02b47a24 */
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_128 + 0x10))(local_128);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = local_68;
  puVar6 = PTR__ZN5Sfs2X4Core16SFSProtocolCodec13UDP_PACKET_IDE_03bd9ac8;
  plVar14 = (long *)*param_2;
                    /* try { // try from 02b46fe0 to 02c4700f has its CatchHandler @ 02b479dc */
  local_140 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec13UDP_PACKET_IDE_03bd9ac8;
  local_138 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec13UDP_PACKET_IDE_03bd9ac8 + 8);
  pcVar16 = *(code **)(*local_68 + 0x48);
  pcVar15 = *(code **)(*plVar14 + 0x18);
  if (local_138 != (long *)0x0) {
    plVar2 = local_138 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  uVar8 = (*pcVar15)(plVar14,&local_140);
  (*pcVar16)(plVar10,uVar8 & 1);
  plVar10 = local_138;
  if (local_138 != (long *)0x0) {
    plVar14 = local_138 + 1;
    do {
      iVar9 = (int)*plVar14 + -1;
                    /* try { // try from 02b47038 to 02c47067 has its CatchHandler @ 02b47994 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_138 + 0x10))(local_138);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  uVar11 = (**(code **)(*local_68 + 0x40))();
  plVar10 = local_68;
                    /* try { // try from 02b4708c to 02c4709b has its CatchHandler @ 02b47e0c */
  if ((uVar11 & 1) != 0) {
    plVar14 = (long *)*param_2;
    local_160 = *(undefined8 *)puVar6;
    local_158 = *(long **)(puVar6 + 8);
    pcVar16 = *(code **)(*local_68 + 0x58);
    pcVar15 = *(code **)(*plVar14 + 0xb8);
    if (local_158 != (long *)0x0) {
      plVar2 = local_158 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar5) {
          *(int *)plVar2 = (int)*plVar2 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
                    /* try { // try from 02b470d0 to 02c470ff has its CatchHandler @ 02b47a20 */
    (*pcVar15)(&local_150,plVar14,&local_160);
    (*pcVar16)(plVar10,*local_150);
    if (local_148 != (long *)0x0) {
      plVar10 = local_148 + 1;
      do {
        iVar9 = (int)*plVar10 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar5) {
          *(int *)plVar10 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_148 + 0x10))(local_148);
        piVar1 = (int *)((long)local_148 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
                    /* try { // try from 02b47128 to 02c47157 has its CatchHandler @ 02b479d8 */
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_148 + 0x18))(local_148);
        }
      }
    }
    plVar10 = local_158;
    if (local_158 != (long *)0x0) {
      plVar14 = local_158 + 1;
      do {
        iVar9 = (int)*plVar14 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar5) {
          *(int *)plVar14 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_158 + 0x10))(local_158);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
                    /* try { // try from 02b47180 to 02c471af has its CatchHandler @ 02b47990 */
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
  }
  plVar10 = (long *)*param_2;
  local_180 = *(undefined8 *)puVar7;
  local_178 = *(long **)(puVar7 + 8);
  pcVar15 = *(code **)(*plVar10 + 0x88);
  if (local_178 != (long *)0x0) {
    plVar14 = local_178 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = (int)*plVar14 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  (*pcVar15)(&local_170,plVar10,&local_180);
  bVar3 = *local_170;
                    /* try { // try from 02b471d4 to 02c471df has its CatchHandler @ 02b47dac */
  if (plStack_168 != (long *)0x0) {
    plVar10 = plStack_168 + 1;
    do {
      iVar9 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plStack_168 + 0x10))(plStack_168);
      piVar1 = (int *)((long)plStack_168 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b47214 to 02c47243 has its CatchHandler @ 02b47a1c */
      if (iVar9 + -1 == 0) {
        (**(code **)(*plStack_168 + 0x18))(plStack_168);
      }
    }
  }
  plVar10 = local_178;
  if (local_178 != (long *)0x0) {
    plVar14 = local_178 + 1;
    do {
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_178 + 0x10))(local_178);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
                    /* try { // try from 02b4726c to 02c4729b has its CatchHandler @ 02b479d4 */
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  _ZN5Sfs2X8Bitswarm14BitSwarmClient13GetControllerEl
            (&local_190,*(undefined8 *)(param_1 + 0x28),(ulong)bVar3);
  if (local_190 != (long *)0x0) {
    pcVar15 = *(code **)(*local_190 + 0x10);
    local_1e0 = local_68;
    local_1d8 = local_60;
    if (local_60 != (long *)0x0) {
      plVar10 = local_60 + 1;
      do {
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar5) {
          *(int *)plVar10 = (int)*plVar10 + 1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
                    /* try { // try from 02b472c4 to 02c472f3 has its CatchHandler @ 02b4798c */
    (*pcVar15)(local_190,&local_1e0);
    plVar10 = local_1d8;
    if (local_1d8 != (long *)0x0) {
      plVar14 = local_1d8 + 1;
      do {
        iVar9 = (int)*plVar14 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar5) {
          *(int *)plVar14 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_1d8 + 0x10))(local_1d8);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
                    /* try { // try from 02b472fc to 02c4730f has its CatchHandler @ 02b487e4 */
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
                    /* try { // try from 02b47310 to 02c4731b has its CatchHandler @ 02b47cd8 */
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    if (local_188 != (long *)0x0) {
      plVar10 = local_188 + 1;
      do {
        iVar9 = (int)*plVar10 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar5) {
          *(int *)plVar10 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
                    /* try { // try from 02b47344 to 02c47353 has its CatchHandler @ 02b47cac */
        (**(code **)(*local_188 + 0x10))(local_188);
        piVar1 = (int *)((long)local_188 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
        } while (cVar4 != '\0');
                    /* try { // try from 02b47364 to 02c47383 has its CatchHandler @ 02b486b4 */
        if (iVar9 + -1 == 0) {
          (**(code **)(*local_188 + 0x18))(local_188);
        }
      }
    }
    plVar10 = local_60;
    if (local_60 != (long *)0x0) {
      plVar14 = local_60 + 1;
      do {
        iVar9 = (int)*plVar14 + -1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
        if (bVar5) {
          *(int *)plVar14 = iVar9;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 == 0) {
        (**(code **)(*local_60 + 0x10))(local_60);
        piVar1 = (int *)((long)plVar10 + 0xc);
        do {
          iVar9 = *piVar1;
          cVar4 = '\x01';
          bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar5) {
            *piVar1 = iVar9 + -1;
            cVar4 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02b473b8 to 02c473e7 has its CatchHandler @ 02b4797c */
        } while (cVar4 != '\0');
        if (iVar9 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
    if (*(long *)(lVar17 + 0x28) == local_58) {
      return;
    }
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  plVar10 = (long *)_Znwm(8);
                    /* try { // try from 02b47410 to 02c4743f has its CatchHandler @ 02b47978 */
  *plVar10 = (long)(PTR_DAT_03c37adf_1_03bd0478 + 0x18);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_1a0,plVar10);
  uVar12 = _Znwm(8);
  FUN_0307a6fc(uVar12,"Cannot handle server response. Unknown controller, id: %d",&local_88);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_1b0,uVar12);
  plVar14 = plStack_198;
  plVar10 = local_1a0;
  if (plStack_198 != (long *)0x0) {
    plVar2 = plStack_198 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b47468 to 02c47497 has its CatchHandler @ 02b47970 */
    } while (cVar4 != '\0');
  }
  if (plStack_1a8 != (long *)0x0) {
    plVar2 = plStack_1a8 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = (int)*plVar2 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  lVar17 = *(long *)(*local_1a0 + -0x18);
  FUN_0307d194(local_1a0,lVar17 + 0x1000,0);
  iVar9 = sprintf((char *)*plVar10,(char *)*local_1b0,(ulong)bVar3);
  if (iVar9 < 0) {
    FUN_0307d194(plVar10,lVar17,0);
  }
  else {
                    /* try { // try from 02b474c0 to 02c474ef has its CatchHandler @ 02b47968 */
    FUN_0307d194(plVar10,lVar17 + iVar9,0);
  }
  if (plStack_1a8 != (long *)0x0) {
    plVar10 = plStack_1a8 + 1;
    do {
      iVar9 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plStack_1a8 + 0x10))(plStack_1a8);
      piVar1 = (int *)((long)plStack_1a8 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plStack_1a8 + 0x18))(plStack_1a8);
      }
    }
  }
                    /* try { // try from 02b47518 to 02c47547 has its CatchHandler @ 02b47964 */
  if (plVar14 != (long *)0x0) {
    plVar10 = plVar14 + 1;
    do {
      iVar9 = (int)*plVar10 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar5) {
        *(int *)plVar10 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*plVar14 + 0x10))(plVar14);
      piVar1 = (int *)((long)plVar14 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*plVar14 + 0x18))(plVar14);
      }
    }
  }
                    /* try { // try from 02b4756c to 02c4757b has its CatchHandler @ 02b47d4c */
  local_1c0 = _Znwm(0x38);
  local_1d0 = local_1a0;
  local_1c8 = plStack_198;
  if (plStack_198 != (long *)0x0) {
    plStack_198 = plStack_198 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plStack_198,0x10);
      if (bVar5) {
        *(int *)plStack_198 = (int)*plStack_198 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  _ZN5Sfs2X10Exceptions13SFSCodecErrorC1EN5boost10shared_ptrISsEE(local_1c0,&local_1d0);
  uStack_1b8 = 0;
                    /* try { // try from 02b475b0 to 02c475df has its CatchHandler @ 02b47a18 */
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions13SFSCodecErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_1c0,local_1c0,(ulong)&local_1c0 | 8);
  plVar10 = local_1c8;
  if (local_1c8 != (long *)0x0) {
    plVar14 = local_1c8 + 1;
    do {
      iVar9 = (int)*plVar14 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar14,0x10);
      if (bVar5) {
        *(int *)plVar14 = iVar9;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_1c8 + 0x10))(local_1c8);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar9 = *piVar1;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar5) {
          *piVar1 = iVar9 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar9 + -1 == 0) {
                    /* try { // try from 02b47608 to 02c47637 has its CatchHandler @ 02b479d0 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  puVar13 = (undefined8 *)__cxa_allocate_exception(0x10);
  uVar12 = uStack_1b8;
  puVar13[1] = 0;
  uStack_1b8 = 0;
  puVar13[1] = uVar12;
  *puVar13 = local_1c0;
  local_1c0 = 0;
                    /* WARNING: Subroutine does not return */
  __cxa_throw(puVar13,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEEE_03bd69c0,
              PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions13SFSCodecErrorEED2Ev_03bd2250);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec12OnPacketReadEN5boost10shared_ptrINS_4Util9ByteArrayEEE
// ADDRESS : 02b482fc
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec12OnPacketReadEN5boost10shared_ptrINS_4Util9ByteArrayEEE
               (undefined8 param_1,undefined8 *param_2)

{
  long *plVar1;
  long *plVar2;
  int *piVar3;
  char cVar4;
  bool bVar5;
  int iVar6;
  long lVar7;
  undefined8 uVar8;
  long *plVar9;
  undefined8 local_78;
  long *plStack_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
                    /* try { // try from 02b48314 to 02c48343 has its CatchHandler @ 02b48348 */
  lVar7 = tpidr_el0;
  local_48 = *(long *)(lVar7 + 0x28);
  local_68 = *param_2;
  local_60 = (long *)param_2[1];
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* catch() { ... } // from try @ 02b48314 with catch @ 02b48348 */
    } while (cVar4 != '\0');
  }
                    /* catch() { ... } // from try @ 02b45c78 with catch @ 02b4834c */
  _ZN5Sfs2X8Entities4Data9SFSObject17NewFromBinaryDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE
            (&local_58,&local_68);
  plVar9 = local_50;
  uVar8 = local_58;
  plVar1 = local_60;
  local_58 = 0;
  local_50 = (long *)0x0;
  if (local_60 != (long *)0x0) {
    plVar2 = local_60 + 1;
    do {
      iVar6 = (int)*plVar2 + -1;
                    /* try { // try from 02b48374 to 02c483a3 has its CatchHandler @ 02b483a8 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar5) {
        *(int *)plVar2 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
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
                    /* catch() { ... } // from try @ 02b48374 with catch @ 02b483a8 */
                    /* catch() { ... } // from try @ 02b459a8 with catch @ 02b483ac */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  local_78 = uVar8;
  plStack_70 = plVar9;
  if (plVar9 != (long *)0x0) {
    plVar1 = plVar9 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b483d4 to 02c48403 has its CatchHandler @ 02b48408 */
  _ZN5Sfs2X4Core16SFSProtocolCodec15DispatchRequestEN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE
            (param_1,&local_78);
  if (plVar9 != (long *)0x0) {
    plVar1 = plVar9 + 1;
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
                    /* catch() { ... } // from try @ 02b483d4 with catch @ 02b48408 */
      (**(code **)(*plVar9 + 0x10))(plVar9);
                    /* catch() { ... } // from try @ 02b46728 with catch @ 02b4840c */
      piVar3 = (int *)((long)plVar9 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02b47728 with catch @ 02b48410 */
        iVar6 = *piVar3;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar3,0x10);
        if (bVar5) {
          *piVar3 = iVar6 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar6 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
    plVar1 = plVar9 + 1;
    do {
      iVar6 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar6;
        cVar4 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b48444 to 02c48473 has its CatchHandler @ 02b48534 */
    } while (cVar4 != '\0');
    if (iVar6 == 0) {
      (**(code **)(*plVar9 + 0x10))(plVar9);
      piVar3 = (int *)((long)plVar9 + 0xc);
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
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  if (*(long *)(lVar7 + 0x28) == local_48) {
                    /* try { // try from 02b484a8 to 02c484d7 has its CatchHandler @ 02b4853c */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
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
// FUNCTION: _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
// ADDRESS : 02b49078
================================================================

void _ZN5Sfs2X4Core16SFSProtocolCodec16PrepareUDPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE
               (undefined8 *param_1,long param_2,undefined8 *param_3)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  undefined1 uVar7;
  undefined8 uVar8;
  long *plVar9;
  code *pcVar10;
  undefined1 auStack_148 [8];
  long *local_140;
  undefined8 local_138;
  long *local_130;
  undefined8 *local_128;
  long *local_120;
  undefined8 local_118;
  long *local_110;
  undefined8 *local_108;
  long *local_100;
  undefined8 local_f8;
  long *local_f0;
  undefined8 local_e8;
  long *local_e0;
  undefined8 *local_d8;
  long *local_d0;
  undefined8 local_c8;
  long *local_c0;
  undefined8 *local_b8;
  long *local_b0;
  undefined8 *local_a8;
  long *local_a0;
  undefined1 *local_98;
  long *local_90;
  undefined8 local_88;
  long *local_80;
  undefined1 *local_78;
  long *local_70;
  long local_68;
  
                    /* try { // try from 02b49088 to 02c49097 has its CatchHandler @ 02b4a390 */
  lVar6 = tpidr_el0;
  local_68 = *(long *)(lVar6 + 0x28);
  uVar8 = _Znwm(0x38);
  _ZN5Sfs2X8Entities4Data9SFSObjectC2Ev();
                    /* try { // try from 02b490c0 to 02c490ef has its CatchHandler @ 02b4a2c8 */
  *param_1 = uVar8;
  param_1[1] = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X8Entities4Data10ISFSObjectENS4_9SFSObjectEEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (param_1,uVar8,param_1 + 1);
  local_78 = (undefined1 *)_Znwm(1);
  *local_78 = 0;
  local_70 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIhhEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_78,local_78,&local_70);
  uVar7 = (**(code **)(*(long *)*param_3 + 0x20))();
  *local_78 = uVar7;
  plVar9 = (long *)*param_1;
                    /* try { // try from 02b49124 to 02c4912b has its CatchHandler @ 02b4a2cc */
  pcVar10 = *(code **)(*plVar9 + 0x1e8);
  local_88 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278;
  local_80 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec13CONTROLLER_IDE_03bd7278 + 8);
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b49154 to 02c49183 has its CatchHandler @ 02b4a2c4 */
  local_98 = local_78;
  local_90 = local_70;
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
  (*pcVar10)(plVar9,&local_88,&local_98);
  plVar9 = local_90;
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
                    /* try { // try from 02b491ac to 02c491db has its CatchHandler @ 02b4a2c0 */
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_80;
  if (local_80 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar2;
                    /* try { // try from 02b49218 to 02c4923f has its CatchHandler @ 02b4a2ac */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  local_a8 = (undefined8 *)_Znwm(8);
                    /* try { // try from 02b49240 to 02c4924b has its CatchHandler @ 02b4a124 */
  *local_a8 = 0;
  local_a0 = (long *)0x0;
                    /* try { // try from 02b4924c to 02c4925f has its CatchHandler @ 02b4a10c */
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_a8,local_a8,&local_a0);
                    /* try { // try from 02b49260 to 02c4926b has its CatchHandler @ 02b4a108 */
  _ZN5Sfs2X8Bitswarm14BitSwarmClient3SfsEv(&local_c8,*(undefined8 *)(param_2 + 0x28));
  _ZN5Sfs2X8SmartFox6MySelfEv(&local_b8,local_c8);
  if (local_b8 == (undefined8 *)0x0) {
    *local_a8 = 0xffffffffffffffff;
  }
  else {
    _ZN5Sfs2X8Bitswarm14BitSwarmClient3SfsEv(&local_e8,*(undefined8 *)(param_2 + 0x28));
    _ZN5Sfs2X8SmartFox6MySelfEv(&local_d8,local_e8);
    uVar8 = (**(code **)*local_d8)();
    *local_a8 = uVar8;
                    /* try { // try from 02b492b0 to 02c492e3 has its CatchHandler @ 02b4a13c */
    if (local_d0 != (long *)0x0) {
      plVar9 = local_d0 + 1;
      do {
        iVar5 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar5;
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
          (**(code **)(*local_d0 + 0x18))(local_d0);
        }
      }
    }
                    /* try { // try from 02b49308 to 02c49337 has its CatchHandler @ 02b49e28 */
    if (local_e0 != (long *)0x0) {
      plVar9 = local_e0 + 1;
      do {
        iVar5 = (int)*plVar9 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar4) {
          *(int *)plVar9 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
        (**(code **)(*local_e0 + 0x10))(local_e0);
        piVar2 = (int *)((long)local_e0 + 0xc);
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
          (**(code **)(*local_e0 + 0x18))(local_e0);
                    /* try { // try from 02b4935c to 02c4938b has its CatchHandler @ 02b49e24 */
        }
      }
    }
  }
  if (local_b0 != (long *)0x0) {
    plVar9 = local_b0 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02b4938c to 02c49397 has its CatchHandler @ 02b4a0f8 */
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar2 = (int *)((long)local_b0 + 0xc);
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
                    /* try { // try from 02b493b8 to 02c493c3 has its CatchHandler @ 02b4a07c */
        (**(code **)(*local_b0 + 0x18))(local_b0);
      }
    }
  }
  if (local_c0 != (long *)0x0) {
    plVar9 = local_c0 + 1;
    do {
                    /* try { // try from 02b493d0 to 02c493db has its CatchHandler @ 02b4a004 */
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_c0 + 0x10))(local_c0);
      piVar2 = (int *)((long)local_c0 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b49404 to 02c49433 has its CatchHandler @ 02b4a134 */
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*local_c0 + 0x18))(local_c0);
      }
    }
  }
  plVar9 = (long *)*param_1;
  pcVar10 = *(code **)(*plVar9 + 0x228);
  local_f8 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec7USER_IDE_03bd2978;
  local_f0 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec7USER_IDE_03bd2978 + 8);
                    /* try { // try from 02b49434 to 02c4944f has its CatchHandler @ 02b48fe8 */
  if (local_f0 != (long *)0x0) {
    plVar1 = local_f0 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b49450 to 02c49463 has its CatchHandler @ 02b49fa0 */
  local_108 = local_a8;
  local_100 = local_a0;
  if (local_a0 != (long *)0x0) {
    plVar1 = local_a0 + 1;
    do {
                    /* try { // try from 02b49468 to 02c4948f has its CatchHandler @ 02b4a138 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar10)(plVar9,&local_f8,&local_108);
  plVar9 = local_100;
  if (local_100 != (long *)0x0) {
    plVar1 = local_100 + 1;
    do {
                    /* try { // try from 02b49490 to 02c4949b has its CatchHandler @ 02b49e14 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b4949c to 02c494af has its CatchHandler @ 02b49dfc */
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02b494b0 to 02c494bb has its CatchHandler @ 02b49df8 */
      (**(code **)(*local_100 + 0x10))(local_100);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_f0;
  if (local_f0 != (long *)0x0) {
    plVar1 = local_f0 + 1;
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
                    /* try { // try from 02b49504 to 02c49533 has its CatchHandler @ 02b49e30 */
      (**(code **)(*local_f0 + 0x10))(local_f0);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  local_b8 = (undefined8 *)_Znwm(8);
  *local_b8 = 0;
  local_b0 = (long *)0x0;
                    /* try { // try from 02b49558 to 02c49587 has its CatchHandler @ 02b49c8c */
  _ZN5boost6detail20sp_pointer_constructIxxEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_b8,local_b8,&local_b0);
  uVar8 = _ZN5Sfs2X8Bitswarm14BitSwarmClient15NextUdpPacketIdEv(*(undefined8 *)(param_2 + 0x28));
  *local_b8 = uVar8;
  plVar9 = (long *)*param_1;
  pcVar10 = *(code **)(*plVar9 + 0x248);
  local_118 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec13UDP_PACKET_IDE_03bd9ac8;
  local_110 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec13UDP_PACKET_IDE_03bd9ac8 + 8);
  if (local_110 != (long *)0x0) {
    plVar1 = local_110 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_128 = local_b8;
  local_120 = local_b0;
                    /* try { // try from 02b495ac to 02c495db has its CatchHandler @ 02b49c88 */
  if (local_b0 != (long *)0x0) {
    plVar1 = local_b0 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar10)(plVar9,&local_118,&local_128);
  plVar9 = local_120;
  if (local_120 != (long *)0x0) {
                    /* try { // try from 02b495dc to 02c495e7 has its CatchHandler @ 02b49de8 */
    plVar1 = local_120 + 1;
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
      (**(code **)(*local_120 + 0x10))(local_120);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
                    /* try { // try from 02b49608 to 02c49613 has its CatchHandler @ 02b49d6c */
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02b49620 to 02c4962b has its CatchHandler @ 02b49cf4 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_110;
  if (local_110 != (long *)0x0) {
    plVar1 = local_110 + 1;
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
                    /* try { // try from 02b49654 to 02c49683 has its CatchHandler @ 02b49e2c */
      (**(code **)(*local_110 + 0x10))(local_110);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
                    /* try { // try from 02b49684 to 02c4969f has its CatchHandler @ 02b48fe8 */
  plVar9 = (long *)*param_1;
  pcVar10 = *(code **)(*plVar9 + 0x378);
  local_138 = *(undefined8 *)PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8;
  local_130 = *(long **)(PTR__ZN5Sfs2X4Core16SFSProtocolCodec8PARAM_IDE_03bd71f8 + 8);
                    /* try { // try from 02b496a0 to 02c496b3 has its CatchHandler @ 02b49c90 */
  if (local_130 != (long *)0x0) {
    plVar1 = local_130 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02b496b4 to 02c496c3 has its CatchHandler @ 02b4a13c */
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02b496c8 to 02c496d7 has its CatchHandler @ 02b49e30 */
  (**(code **)(*(long *)*param_3 + 0x10))(auStack_148);
  (*pcVar10)(plVar9,&local_138,auStack_148);
                    /* try { // try from 02b496dc to 02c49703 has its CatchHandler @ 02b49c74 */
  if (local_140 != (long *)0x0) {
    plVar9 = local_140 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02b49704 to 02c4970f has its CatchHandler @ 02b49ae0 */
      (**(code **)(*local_140 + 0x10))(local_140);
      piVar2 = (int *)((long)local_140 + 0xc);
      do {
                    /* try { // try from 02b49710 to 02c49723 has its CatchHandler @ 02b49ac4 */
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02b49724 to 02c4972f has its CatchHandler @ 02b49ac0 */
        (**(code **)(*local_140 + 0x18))(local_140);
      }
    }
  }
  plVar9 = local_130;
  if (local_130 != (long *)0x0) {
    plVar1 = local_130 + 1;
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
      (**(code **)(*local_130 + 0x10))(local_130);
      piVar2 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b49774 to 02c497b7 has its CatchHandler @ 02b49af8 */
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_b0;
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
      (**(code **)(*local_b0 + 0x10))(local_b0);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
                    /* try { // try from 02b497dc to 02c4980b has its CatchHandler @ 02b49944 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_a0;
  if (local_a0 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar9 + 0xc);
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
                    /* try { // try from 02b49830 to 02c4985f has its CatchHandler @ 02b49940 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  plVar9 = local_70;
  if (local_70 != (long *)0x0) {
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
                    /* try { // try from 02b49860 to 02c4986b has its CatchHandler @ 02b49aac */
      (**(code **)(*local_70 + 0x10))(local_70);
      piVar2 = (int *)((long)plVar9 + 0xc);
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
                    /* try { // try from 02b4988c to 02c49897 has its CatchHandler @ 02b49a2c */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_68) {
                    /* try { // try from 02b498a4 to 02c498af has its CatchHandler @ 02b499b0 */
    return;
  }
                    /* WARNING: Subroutine does not return */
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



================================================================
// FUNCTION: _ZN5Sfs2X4Util22DelegateThreeArgumentsIN5boost10shared_ptrINS_4Core12PacketHeaderEEENS3_INS0_9ByteArrayEEEbE6InvokeES6_S8_b
// ADDRESS : 02b70858
================================================================

void _ZN5Sfs2X4Util22DelegateThreeArgumentsIN5boost10shared_ptrINS_4Core12PacketHeaderEEENS3_INS0_9ByteArrayEEEbE6InvokeES6_S8_b
               (undefined8 *param_1,undefined8 *param_2,undefined8 *param_3,uint param_4)

{
  long *plVar1;
  long *plVar2;
  int *piVar3;
  code *pcVar4;
  undefined8 uVar5;
  char cVar6;
  bool bVar7;
  int iVar8;
  long lVar9;
  undefined8 local_48;
  long *local_40;
  undefined8 local_38;
  long *local_30;
  long local_28;
  
  lVar9 = tpidr_el0;
  local_28 = *(long *)(lVar9 + 0x28);
  local_38 = *param_2;
  pcVar4 = (code *)*param_1;
  uVar5 = param_1[1];
  local_30 = (long *)param_2[1];
  if (local_30 != (long *)0x0) {
    plVar1 = local_30 + 1;
    do {
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar7) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
  }
  local_48 = *param_3;
                    /* try { // try from 02b708a4 to 02c708d3 has its CatchHandler @ 02b709c4 */
  local_40 = (long *)param_3[1];
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar7) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
  }
  (*pcVar4)(uVar5,&local_38,&local_48,param_4 & 1);
  plVar1 = local_40;
  if (local_40 != (long *)0x0) {
    plVar2 = local_40 + 1;
    do {
      iVar8 = (int)*plVar2 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar7) {
        *(int *)plVar2 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02b708fc to 02c7092b has its CatchHandler @ 02b709c8 */
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar3 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar3;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar3,0x10);
        if (bVar7) {
          *piVar3 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  plVar1 = local_30;
  if (local_30 != (long *)0x0) {
    plVar2 = local_30 + 1;
    do {
      iVar8 = (int)*plVar2 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar2,0x10);
      if (bVar7) {
        *(int *)plVar2 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02b70950 to 02c7097f has its CatchHandler @ 02b709cc */
      (**(code **)(*local_30 + 0x10))(local_30);
      piVar3 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar3;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar3,0x10);
        if (bVar7) {
          *piVar3 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02b70980 to 02c709cf has its CatchHandler @ 02b6f770 */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (*(long *)(lVar9 + 0x28) == local_28) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE
// ADDRESS : 02b71a4c
================================================================

void _ZN5Sfs2X4Core13ThreadManager11EnqueueSendEN5boost10shared_ptrINS_4Util22DelegateThreeArgumentsINS3_INS0_12PacketHeaderEEENS3_INS4_9ByteArrayEEEbEEEES7_S9_NS3_IbEE
               (long param_1,undefined8 *param_2,undefined8 *param_3,undefined8 *param_4,
               undefined8 *param_5)

{
  long *plVar1;
  undefined *puVar2;
  long *plVar3;
  char cVar4;
  bool bVar5;
  long lVar6;
  uint uVar7;
  int iVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  ulong uVar12;
  int *piVar13;
  undefined8 *puVar14;
  size_t sVar15;
  undefined8 uVar16;
  undefined1 auVar17 [16];
  undefined *local_a0;
  undefined8 uStack_98;
  long *local_90;
  long local_80;
  long *local_78;
  undefined1 auStack_70 [8];
  long local_68;
  
                    /* try { // try from 02b71a60 to 02c71a9f has its CatchHandler @ 02b719a4 */
  lVar6 = tpidr_el0;
  local_68 = *(long *)(lVar6 + 0x28);
  lVar9 = _Znwm(0x30);
  *(undefined8 *)(lVar9 + 0x10) = 0;
  *(undefined8 *)(lVar9 + 0x18) = 0;
                    /* try { // try from 02b71aa0 to 02c71acf has its CatchHandler @ 02b71d00 */
  *(undefined8 *)(lVar9 + 0x20) = 0;
  *(undefined8 *)(lVar9 + 0x28) = 0;
  puVar14 = (undefined8 *)(lVar9 + 8);
  *puVar14 = 0;
  *(undefined8 **)(lVar9 + 0x18) = puVar14;
  *(undefined8 **)(lVar9 + 0x20) = puVar14;
  _ZN5boost10shared_ptrISt3mapISsNS0_IvEESt4lessISsESaISt4pairIKSsS2_EEEEC2IS9_EEPT_
            (&local_80,lVar9);
  lVar9 = local_80;
  FUN_0307a6fc(&local_a0,"callback",auStack_70);
                    /* try { // try from 02b71ad0 to 02c71afb has its CatchHandler @ 02b719a4 */
  uStack_98 = *param_2;
  local_90 = (long *)param_2[1];
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b71afc to 02c71b03 has its CatchHandler @ 02b71d08 */
  auVar17 = FUN_027b61f4(lVar9,&local_a0);
  lVar11 = auVar17._8_8_;
  if (lVar11 != 0) {
    if ((auVar17._0_8_ == 0) && (lVar9 + 8 != lVar11)) {
      uVar12 = *(ulong *)(local_a0 + -0x18);
      sVar15 = *(ulong *)((long)*(void **)(lVar11 + 0x20) + -0x18);
      lVar10 = uVar12 - sVar15;
      if (uVar12 < sVar15 || lVar10 == 0) {
        sVar15 = uVar12;
      }
      uVar7 = memcmp(local_a0,*(void **)(lVar11 + 0x20),sVar15);
      uVar12 = (ulong)uVar7;
      if ((uVar7 == 0) && (uVar12 = 0, lVar10 < 0x80000000)) {
        uVar7 = (uint)lVar10;
        if (lVar10 < -0x7fffffff) {
          uVar7 = 0x80000000;
        }
        uVar12 = (ulong)uVar7;
      }
      uVar12 = uVar12 >> 0x1f;
    }
    else {
      uVar12 = 1;
    }
    lVar10 = _Znwm(0x38);
    plVar1 = local_90;
    uVar16 = uStack_98;
                    /* try { // try from 02b71b78 to 02c71ba7 has its CatchHandler @ 02b71cfc */
    puVar2 = PTR_DAT_03c37adf_1_03bd0478 + 0x18;
    uStack_98 = 0;
    local_90 = (long *)0x0;
    *(undefined8 *)(lVar10 + 0x28) = uVar16;
    *(undefined **)(lVar10 + 0x20) = local_a0;
    *(long **)(lVar10 + 0x30) = plVar1;
    local_a0 = puVar2;
    FUN_0306006c(uVar12,lVar10,lVar11,lVar9 + 8);
    *(long *)(lVar9 + 0x28) = *(long *)(lVar9 + 0x28) + 1;
  }
  plVar1 = local_90;
  if (local_90 != (long *)0x0) {
    plVar3 = local_90 + 1;
    do {
      iVar8 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar8;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b71bd0 to 02c71bff has its CatchHandler @ 02b71cf8 */
    if (iVar8 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar13 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  puVar2 = PTR_DAT_03c37adf_1_03bd0478;
  if (local_a0 + -0x18 != PTR_DAT_03c37adf_1_03bd0478) {
    piVar13 = (int *)(local_a0 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar8 = *piVar13;
      *piVar13 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02b72130 to 02c7215f has its CatchHandler @ 02b7220c */
      } while (cVar4 != '\0');
    }
    if (iVar8 < 1) {
      _ZdlPv(local_a0 + -0x18);
    }
  }
  lVar9 = local_80;
                    /* try { // try from 02b71c28 to 02c71c57 has its CatchHandler @ 02b71cf4 */
  FUN_0307a6fc(&local_a0,"header",auStack_70);
  uStack_98 = *param_3;
  local_90 = (long *)param_3[1];
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
                    /* try { // try from 02b71c58 to 02c71c83 has its CatchHandler @ 02b719a4 */
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  auVar17 = FUN_027b61f4(lVar9,&local_a0);
  lVar11 = auVar17._8_8_;
  if (lVar11 != 0) {
                    /* try { // try from 02b71c84 to 02c71c8f has its CatchHandler @ 02b71c90 */
    if ((auVar17._0_8_ == 0) && (lVar9 + 8 != lVar11)) {
                    /* catch() { ... } // from try @ 02b71c84 with catch @ 02b71c90 */
      uVar12 = *(ulong *)(local_a0 + -0x18);
      sVar15 = *(ulong *)((long)*(void **)(lVar11 + 0x20) + -0x18);
      lVar10 = uVar12 - sVar15;
      if (uVar12 < sVar15 || lVar10 == 0) {
        sVar15 = uVar12;
      }
      uVar7 = memcmp(local_a0,*(void **)(lVar11 + 0x20),sVar15);
      uVar12 = (ulong)uVar7;
      if ((uVar7 == 0) && (uVar12 = 0, lVar10 < 0x80000000)) {
                    /* try { // try from 02b71cbc to 02c71ceb has its CatchHandler @ 02b71cf0 */
        uVar7 = (uint)lVar10;
        if (lVar10 < -0x7fffffff) {
          uVar7 = 0x80000000;
        }
        uVar12 = (ulong)uVar7;
      }
      uVar12 = uVar12 >> 0x1f;
    }
    else {
      uVar12 = 1;
    }
    lVar10 = _Znwm(0x38);
    plVar1 = local_90;
    uVar16 = uStack_98;
    uStack_98 = 0;
                    /* catch() { ... } // from try @ 02b71cbc with catch @ 02b71cf0 */
                    /* catch() { ... } // from try @ 02b71c28 with catch @ 02b71cf4 */
                    /* catch() { ... } // from try @ 02b71bd0 with catch @ 02b71cf8 */
                    /* catch() { ... } // from try @ 02b71b78 with catch @ 02b71cfc */
    local_90 = (long *)0x0;
                    /* catch() { ... } // from try @ 02b71aa0 with catch @ 02b71d00 */
    *(undefined8 *)(lVar10 + 0x28) = uVar16;
    *(undefined **)(lVar10 + 0x20) = local_a0;
                    /* catch() { ... } // from try @ 02b71a30 with catch @ 02b71d04 */
    *(long **)(lVar10 + 0x30) = plVar1;
    local_a0 = puVar2 + 0x18;
                    /* catch() { ... } // from try @ 02b71afc with catch @ 02b71d08 */
    FUN_0306006c(uVar12,lVar10,lVar11,lVar9 + 8);
    *(long *)(lVar9 + 0x28) = *(long *)(lVar9 + 0x28) + 1;
  }
  plVar1 = local_90;
  if (local_90 != (long *)0x0) {
    plVar3 = local_90 + 1;
    do {
      iVar8 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar8;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b71d34 to 02c71d63 has its CatchHandler @ 02b71d68 */
    if (iVar8 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar13 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar8 + -1 == 0) {
                    /* catch() { ... } // from try @ 02b71d34 with catch @ 02b71d68 */
                    /* catch() { ... } // from try @ 02b71a00 with catch @ 02b71d6c */
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (local_a0 + -0x18 != puVar2) {
    piVar13 = (int *)(local_a0 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar8 = *piVar13;
      *piVar13 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    if (iVar8 < 1) {
      _ZdlPv(local_a0 + -0x18);
    }
  }
  lVar9 = local_80;
  FUN_0307a6fc(&local_a0,"data",auStack_70);
                    /* try { // try from 02b71d98 to 02c71dc7 has its CatchHandler @ 02b71dd0 */
  uStack_98 = *param_4;
  local_90 = (long *)param_4[1];
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
                    /* try { // try from 02b71dc8 to 02c71dd3 has its CatchHandler @ 02b719a4 */
  auVar17 = FUN_027b61f4(lVar9,&local_a0);
  lVar11 = auVar17._8_8_;
                    /* catch() { ... } // from try @ 02b71d98 with catch @ 02b71dd0 */
  if (lVar11 != 0) {
    if ((auVar17._0_8_ == 0) && (lVar9 + 8 != lVar11)) {
      uVar12 = *(ulong *)(local_a0 + -0x18);
      sVar15 = *(ulong *)((long)*(void **)(lVar11 + 0x20) + -0x18);
      lVar10 = uVar12 - sVar15;
      if (uVar12 < sVar15 || lVar10 == 0) {
        sVar15 = uVar12;
      }
      uVar7 = memcmp(local_a0,*(void **)(lVar11 + 0x20),sVar15);
      uVar12 = (ulong)uVar7;
      if ((uVar7 == 0) && (uVar12 = 0, lVar10 < 0x80000000)) {
        uVar7 = (uint)lVar10;
        if (lVar10 < -0x7fffffff) {
          uVar7 = 0x80000000;
        }
        uVar12 = (ulong)uVar7;
      }
      uVar12 = uVar12 >> 0x1f;
    }
    else {
      uVar12 = 1;
    }
    lVar10 = _Znwm(0x38);
    plVar1 = local_90;
    uVar16 = uStack_98;
    uStack_98 = 0;
    local_90 = (long *)0x0;
    *(undefined8 *)(lVar10 + 0x28) = uVar16;
    *(undefined **)(lVar10 + 0x20) = local_a0;
    *(long **)(lVar10 + 0x30) = plVar1;
    local_a0 = puVar2 + 0x18;
    FUN_0306006c(uVar12,lVar10,lVar11,lVar9 + 8);
    *(long *)(lVar9 + 0x28) = *(long *)(lVar9 + 0x28) + 1;
  }
  plVar1 = local_90;
  if (local_90 != (long *)0x0) {
    plVar3 = local_90 + 1;
    do {
      iVar8 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar8;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar13 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (local_a0 + -0x18 != puVar2) {
                    /* try { // try from 02b72160 to 02c7224f has its CatchHandler @ 02b71f40 */
    piVar13 = (int *)(local_a0 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar8 = *piVar13;
      *piVar13 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
    if (iVar8 < 1) {
      _ZdlPv(local_a0 + -0x18);
    }
  }
  lVar9 = local_80;
  FUN_0307a6fc(&local_a0,&DAT_03243f6b,auStack_70);
  uStack_98 = *param_5;
  local_90 = (long *)param_5[1];
  if (local_90 != (long *)0x0) {
    plVar1 = local_90 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  auVar17 = FUN_027b61f4(lVar9,&local_a0);
  lVar11 = auVar17._8_8_;
  if (lVar11 != 0) {
    if ((auVar17._0_8_ == 0) && (lVar9 + 8 != lVar11)) {
                    /* try { // try from 02b71f40 to 02c71f77 has its CatchHandler @ 02b71f40
                       catch() { ... } // from try @ 02b71f40 with catch @ 02b71f40
                       catch() { ... } // from try @ 02b72160 with catch @ 02b71f40
                       catch() { ... } // from try @ 02b72498 with catch @ 02b71f40 */
      uVar12 = *(ulong *)(local_a0 + -0x18);
      sVar15 = *(ulong *)((long)*(void **)(lVar11 + 0x20) + -0x18);
      lVar10 = uVar12 - sVar15;
      if (uVar12 < sVar15 || lVar10 == 0) {
        sVar15 = uVar12;
      }
      uVar7 = memcmp(local_a0,*(void **)(lVar11 + 0x20),sVar15);
      uVar12 = (ulong)uVar7;
      if ((uVar7 == 0) && (uVar12 = 0, lVar10 < 0x80000000)) {
                    /* try { // try from 02b71f78 to 02c71f83 has its CatchHandler @ 02b724a8 */
        uVar7 = (uint)lVar10;
        if (lVar10 < -0x7fffffff) {
          uVar7 = 0x80000000;
        }
        uVar12 = (ulong)uVar7;
      }
      uVar12 = uVar12 >> 0x1f;
    }
    else {
      uVar12 = 1;
    }
                    /* try { // try from 02b71f88 to 02c71f8f has its CatchHandler @ 02b72438 */
    lVar10 = _Znwm(0x38);
    plVar1 = local_90;
    uVar16 = uStack_98;
                    /* try { // try from 02b71f98 to 02c71f9f has its CatchHandler @ 02b7221c */
    uStack_98 = 0;
                    /* try { // try from 02b71fa8 to 02c71fbb has its CatchHandler @ 02b72218 */
    local_90 = (long *)0x0;
    *(undefined8 *)(lVar10 + 0x28) = uVar16;
    *(undefined **)(lVar10 + 0x20) = local_a0;
    *(long **)(lVar10 + 0x30) = plVar1;
    local_a0 = puVar2 + 0x18;
    FUN_0306006c(uVar12,lVar10,lVar11,lVar9 + 8);
                    /* try { // try from 02b71fc4 to 02c71fcb has its CatchHandler @ 02b723a4 */
                    /* try { // try from 02b71fcc to 02c71fdf has its CatchHandler @ 02b72358 */
    *(long *)(lVar9 + 0x28) = *(long *)(lVar9 + 0x28) + 1;
  }
  plVar1 = local_90;
  if (local_90 != (long *)0x0) {
    plVar3 = local_90 + 1;
    do {
      iVar8 = (int)*plVar3 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar3,0x10);
      if (bVar5) {
        *(int *)plVar3 = iVar8;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b71fec to 02c71ff7 has its CatchHandler @ 02b722e4 */
    if (iVar8 == 0) {
      (**(code **)(*local_90 + 0x10))(local_90);
      piVar13 = (int *)((long)plVar1 + 0xc);
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar1 + 0x18))(plVar1);
      }
    }
  }
  if (local_a0 + -0x18 != puVar2) {
    piVar13 = (int *)(local_a0 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar8 = *piVar13;
                    /* catch() { ... } // from try @ 02b72130 with catch @ 02b7220c */
      *piVar13 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
    }
                    /* catch() { ... } // from try @ 02b720d8 with catch @ 02b72210 */
                    /* catch() { ... } // from try @ 02b72058 with catch @ 02b72214 */
    if (iVar8 < 1) {
                    /* catch() { ... } // from try @ 02b71fa8 with catch @ 02b72218 */
                    /* catch() { ... } // from try @ 02b71f98 with catch @ 02b7221c */
      _ZdlPv(local_a0 + -0x18);
    }
  }
  _ZN5boost5mutex4lockEv((pthread_mutex_t *)(param_1 + 0x70));
  uVar16 = *(undefined8 *)(param_1 + 0x60);
  puVar14 = (undefined8 *)_Znwm(0x20);
  *puVar14 = 0;
  puVar14[1] = 0;
                    /* try { // try from 02b72058 to 02c72087 has its CatchHandler @ 02b72214 */
  puVar14[2] = local_80;
  puVar14[3] = local_78;
  if (local_78 != (long *)0x0) {
    plVar1 = local_78 + 1;
    do {
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
  }
  FUN_0303d178(puVar14,uVar16);
  do {
    iVar8 = pthread_mutex_unlock((pthread_mutex_t *)(param_1 + 0x70));
  } while (iVar8 == 4);
  if (local_78 != (long *)0x0) {
    plVar1 = local_78 + 1;
    do {
      iVar8 = (int)*plVar1 + -1;
      cVar4 = '\x01';
      bVar5 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar5) {
        *(int *)plVar1 = iVar8;
        cVar4 = ExclusiveMonitorsStatus();
      }
    } while (cVar4 != '\0');
                    /* try { // try from 02b720a8 to 02c720b3 has its CatchHandler @ 02b72228 */
    if (iVar8 == 0) {
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar13 = (int *)((long)local_78 + 0xc);
      do {
        iVar8 = *piVar13;
        cVar4 = '\x01';
        bVar5 = (bool)ExclusiveMonitorPass(piVar13,0x10);
        if (bVar5) {
          *piVar13 = iVar8 + -1;
          cVar4 = ExclusiveMonitorsStatus();
        }
      } while (cVar4 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02b720d8 to 02c72107 has its CatchHandler @ 02b72210 */
        (**(code **)(*local_78 + 0x18))(local_78);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) != local_68) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequestC2Ev
// ADDRESS : 02bbd8e4
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequestC2Ev(long *param_1)

{
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,7);
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests21GenericMessageRequestE_03bd08f0 + 0x10);
  memset(param_1 + 0xf,0,0x50);
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  param_1[0xc] = 0;
  param_1[0xd] = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  param_1[0x16] = 0;
  param_1[0x17] = 0;
  param_1[6] = -1;
  param_1[7] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequestD1Ev
// ADDRESS : 02bbd954
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequestD1Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  char cVar6;
  bool bVar7;
  int iVar8;
  long *plVar9;
  long *plVar10;
  
                    /* catch() { ... } // from try @ 02bbda08 with catch @ 02bbd968 */
  plVar10 = (long *)param_1[0x17];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests21GenericMessageRequestE_03bd08f0 + 0x10);
  if (plVar10 != (long *)0x0) {
    lVar5 = plVar10[1];
    lVar4 = *plVar10;
    for (lVar3 = lVar4; lVar5 != lVar3; lVar3 = lVar3 + 0x10) {
      plVar9 = *(long **)(lVar3 + 8);
      if (plVar9 != (long *)0x0) {
        plVar1 = plVar9 + 1;
        do {
          iVar8 = (int)*plVar1 + -1;
          cVar6 = '\x01';
          bVar7 = (bool)ExclusiveMonitorPass(plVar1,0x10);
          if (bVar7) {
            *(int *)plVar1 = iVar8;
            cVar6 = ExclusiveMonitorsStatus();
          }
        } while (cVar6 != '\0');
        if (iVar8 == 0) {
          (**(code **)(*plVar9 + 0x10))(plVar9);
          piVar2 = (int *)((long)plVar9 + 0xc);
          do {
            iVar8 = *piVar2;
            cVar6 = '\x01';
            bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
            if (bVar7) {
              *piVar2 = iVar8 + -1;
              cVar6 = ExclusiveMonitorsStatus();
            }
          } while (cVar6 != '\0');
                    /* try { // try from 02bbd9d8 to 02cbda07 has its CatchHandler @ 02bbdaa8 */
          if (iVar8 + -1 == 0) {
            (**(code **)(*plVar9 + 0x18))(plVar9);
          }
        }
      }
    }
    plVar10[1] = lVar4;
    plVar10 = (long *)param_1[0x18];
    param_1[0x17] = 0;
    param_1[0x18] = 0;
    if (plVar10 != (long *)0x0) {
                    /* try { // try from 02bbda08 to 02cbdaab has its CatchHandler @ 02bbd968 */
      plVar9 = plVar10 + 1;
      do {
        iVar8 = (int)*plVar9 + -1;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar7) {
          *(int *)plVar9 = iVar8;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 == 0) {
        (**(code **)(*plVar10 + 0x10))(plVar10);
        piVar2 = (int *)((long)plVar10 + 0xc);
        do {
          iVar8 = *piVar2;
          cVar6 = '\x01';
          bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar7) {
            *piVar2 = iVar8 + -1;
            cVar6 = ExclusiveMonitorsStatus();
          }
        } while (cVar6 != '\0');
        if (iVar8 + -1 == 0) {
          (**(code **)(*plVar10 + 0x18))(plVar10);
        }
      }
    }
  }
  plVar10 = (long *)param_1[0x18];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbd9d8 with catch @ 02bbdaa8 */
                    /* catch() { ... } // from try @ 02bbdb80 with catch @ 02bbdaac
                       catch() { ... } // from try @ 02bbdd80 with catch @ 02bbdaac */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x16];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x14];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
                    /* try { // try from 02bbdb18 to 02cbdb2b has its CatchHandler @ 02bbdbac */
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* try { // try from 02bbdb50 to 02cbdb7f has its CatchHandler @ 02bbdba8 */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x12];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdb80 to 02cbdbe3 has its CatchHandler @ 02bbdaac */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbdb50 with catch @ 02bbdba8 */
                    /* catch() { ... } // from try @ 02bbdb18 with catch @ 02bbdbac */
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0x10];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdbe4 to 02cbdc0f has its CatchHandler @ 02bbdd94 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0xe];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
                    /* try { // try from 02bbdc3c to 02cbdc6b has its CatchHandler @ 02bbdd90 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[0xc];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
                    /* try { // try from 02bbdc98 to 02cbdcc7 has its CatchHandler @ 02bbdd8c */
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[10];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
                    /* try { // try from 02bbdcf4 to 02cbdd23 has its CatchHandler @ 02bbdd88 */
        iVar8 = *piVar2;
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar10 = (long *)param_1[8];
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar8 = (int)*plVar9 + -1;
      cVar6 = '\x01';
      bVar7 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar7) {
        *(int *)plVar9 = iVar8;
        cVar6 = ExclusiveMonitorsStatus();
      }
    } while (cVar6 != '\0');
    if (iVar8 == 0) {
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar2 = (int *)((long)plVar10 + 0xc);
      do {
        iVar8 = *piVar2;
                    /* try { // try from 02bbdd50 to 02cbdd7f has its CatchHandler @ 02bbdd98 */
        cVar6 = '\x01';
        bVar7 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar7) {
          *piVar2 = iVar8 + -1;
          cVar6 = ExclusiveMonitorsStatus();
        }
      } while (cVar6 != '\0');
      if (iVar8 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
                    /* try { // try from 02bbdd80 to 02cbdd9b has its CatchHandler @ 02bbdaac */
  _ZN5Sfs2X8Requests11BaseRequestD1Ev(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequestD0Ev
// ADDRESS : 02bbddb4
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequestD0Ev(void *param_1)

{
  _ZN5Sfs2X8Requests21GenericMessageRequestD1Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bbddd8
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest8ValidateEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  undefined *puVar4;
  long lVar5;
  long lVar6;
  undefined8 uVar7;
  undefined8 *puVar8;
  undefined8 extraout_x1;
  undefined **ppuVar9;
  int *piVar10;
  int iVar11;
  long *plVar12;
  long *plVar13;
  long *local_160;
  long *local_158;
  long local_150;
  long *local_148;
  undefined8 local_140;
  undefined8 uStack_138;
  long local_130;
  long *plStack_128;
  long *local_120;
  long *plStack_118;
  long *local_110;
  long *plStack_108;
  undefined8 local_100;
  long *local_f8;
  long *local_f0;
  long *plStack_e8;
  long *local_e0;
  long *plStack_d8;
  long *local_d0;
  long *plStack_c8;
  undefined8 local_c0;
  long *local_b8;
  long *local_b0;
  long *local_a8;
  undefined8 local_a0;
  long *local_98;
  undefined *local_90;
  long *local_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined *local_68;
  long *plStack_60;
  undefined8 local_58;
  long *plStack_50;
  long local_48;
  
  lVar6 = tpidr_el0;
  local_48 = *(long *)(lVar6 + 0x28);
  if (*(long *)(param_1 + 0x30) < 0) {
    lVar6 = _Znwm(0x10);
    *(long *)lVar6 = lVar6;
    *(long *)(lVar6 + 8) = lVar6;
    _ZN5boost10shared_ptrISt4listISsSaISsEEEC2IS3_EEPT_(&local_58,lVar6);
    uVar7 = local_58;
                    /* try { // try from 02bbdf74 to 02cbdfa3 has its CatchHandler @ 02bbe248 */
    FUN_0307a6fc(&local_68,"Unsupported message type: " + *(long *)(param_1 + 0x30),&local_b0);
    puVar8 = (undefined8 *)_Znwm(0x18);
    *puVar8 = 0;
    puVar8[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bbdfa4 to 02cbdfb3 has its CatchHandler @ 02bbdd9c */
    puVar8[2] = local_68;
    local_68 = puVar4 + 0x18;
    FUN_0303d178(puVar8,uVar7);
                    /* try { // try from 02bbdfb4 to 02cbdfbf has its CatchHandler @ 02bbe2bc */
    if (local_68 + -0x18 != puVar4) {
      piVar10 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar11 = *piVar10;
        *piVar10 = iVar11 + -1;
      }
      else {
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      if (iVar11 < 1) {
        _ZdlPv(local_68 + -0x18);
      }
    }
    uVar7 = _Znwm(8);
                    /* try { // try from 02bbdfd0 to 02cbdfdb has its CatchHandler @ 02bbe258 */
    FUN_0307a6fc(uVar7,"PublicMessage request error",&local_80);
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_68,uVar7);
    local_80 = _Znwm(0x48);
    ppuVar9 = &local_68;
    local_90 = local_68;
    local_88 = plStack_60;
    if (plStack_60 != (long *)0x0) {
      plStack_60 = plStack_60 + 1;
      do {
                    /* try { // try from 02bbe010 to 02cbe03f has its CatchHandler @ 02bbe244 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plStack_60,0x10);
        if (bVar3) {
          *(int *)plStack_60 = (int)*plStack_60 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_a0 = local_58;
    local_98 = plStack_50;
    if (plStack_50 != (long *)0x0) {
      ppuVar9 = (undefined **)(plStack_50 + 1);
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(ppuVar9,0x10);
        if (bVar3) {
          *(int *)ppuVar9 = *(int *)ppuVar9 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X10Exceptions18SFSValidationErrorC2EN5boost10shared_ptrISsEENS3_ISt4listISsSaISsEEEE
              (ppuVar9,local_80,&local_90,&local_a0);
    uStack_78 = 0;
                    /* try { // try from 02bbe068 to 02cbe097 has its CatchHandler @ 02bbe240 */
    _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions18SFSValidationErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_80,local_80,(ulong)&local_80 | 8);
    plVar12 = local_98;
    if (local_98 != (long *)0x0) {
      plVar13 = local_98 + 1;
      do {
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
                    /* try { // try from 02bbe098 to 02cbe0ab has its CatchHandler @ 02bbdd9c */
        (**(code **)(*local_98 + 0x10))(local_98);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02bbe0ac to 02cbe0cf has its CatchHandler @ 02bbe324 */
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    plVar12 = local_88;
    if (local_88 != (long *)0x0) {
      plVar13 = local_88 + 1;
      do {
                    /* try { // try from 02bbe0d0 to 02cbe17f has its CatchHandler @ 02bbdd9c */
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_88 + 0x10))(local_88);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    puVar8 = (undefined8 *)__cxa_allocate_exception(0x10);
    uVar7 = uStack_78;
    puVar8[1] = 0;
    uStack_78 = 0;
    puVar8[1] = uVar7;
    *puVar8 = local_80;
    local_80 = 0;
                    /* WARNING: Subroutine does not return */
    __cxa_throw(puVar8,
                PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEEE_03bd18c8,
                PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEED2Ev_03bd87c0);
  }
  lVar5 = _Znwm(0x10);
  *(long *)lVar5 = lVar5;
  *(long *)(lVar5 + 8) = lVar5;
                    /* try { // try from 02bbde24 to 02cbde53 has its CatchHandler @ 02bbe254 */
  _ZN5boost10shared_ptrISt4listISsSaISsEEEC2IS3_EEPT_(&local_b0,lVar5);
  plVar12 = local_a8;
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    local_c0 = *param_2;
    local_b8 = (long *)param_2[1];
                    /* try { // try from 02bbde54 to 02cbde67 has its CatchHandler @ 02bbdd9c */
    if (local_b8 != (long *)0x0) {
      plVar13 = local_b8 + 1;
      do {
                    /* try { // try from 02bbde68 to 02cbde73 has its CatchHandler @ 02bbe2c0 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = (int)*plVar13 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_d0 = local_b0;
    plStack_c8 = local_a8;
    if (local_a8 != (long *)0x0) {
      plVar13 = local_a8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = (int)*plVar13 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
              (param_1,&local_c0,&local_d0);
    if (plVar12 != (long *)0x0) {
      plVar13 = plVar12 + 1;
      do {
                    /* try { // try from 02bbdea8 to 02cbded7 has its CatchHandler @ 02bbe250 */
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*plVar12 + 0x10))(plVar12);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    plVar12 = local_b8;
    if (local_b8 != (long *)0x0) {
      plVar13 = local_b8 + 1;
      do {
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
                    /* try { // try from 02bbdf1c to 02cbdf4b has its CatchHandler @ 02bbe24c */
        (**(code **)(*local_b8 + 0x10))(local_b8);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    break;
  case 1:
                    /* catch() { ... } // from try @ 02bbe010 with catch @ 02bbe244 */
    plVar13 = (long *)param_2[1];
                    /* catch() { ... } // from try @ 02bbdf74 with catch @ 02bbe248 */
    if (plVar13 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bbdf1c with catch @ 02bbe24c */
      plVar1 = plVar13 + 1;
      do {
                    /* catch() { ... } // from try @ 02bbdea8 with catch @ 02bbe250 */
                    /* catch() { ... } // from try @ 02bbde24 with catch @ 02bbe254 */
                    /* catch() { ... } // from try @ 02bbdfd0 with catch @ 02bbe258 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_e0 = local_b0;
    plStack_d8 = local_a8;
    if (local_a8 != (long *)0x0) {
      plVar1 = local_a8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
                    /* try { // try from 02bbe284 to 02cbe2b3 has its CatchHandler @ 02bbe2b8 */
    _ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
              (param_1,extraout_x1,&local_e0);
    if (plVar12 != (long *)0x0) {
      plVar1 = plVar12 + 1;
      do {
        iVar11 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*plVar12 + 0x10))(plVar12);
                    /* catch() { ... } // from try @ 02bbe284 with catch @ 02bbe2b8 */
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
                    /* catch() { ... } // from try @ 02bbdfb4 with catch @ 02bbe2bc */
          iVar11 = *piVar10;
                    /* catch() { ... } // from try @ 02bbde68 with catch @ 02bbe2c0 */
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    if (plVar13 != (long *)0x0) {
      plVar12 = plVar13 + 1;
      do {
                    /* try { // try from 02bbe2ec to 02cbe31b has its CatchHandler @ 02bbe320 */
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*plVar13 + 0x10))(plVar13);
        piVar10 = (int *)((long)plVar13 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02bbe31c to 02cbe337 has its CatchHandler @ 02bbdd9c */
        } while (cVar2 != '\0');
                    /* catch() { ... } // from try @ 02bbe2ec with catch @ 02bbe320 */
        if (iVar11 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbe0ac with catch @ 02bbe324 */
          (**(code **)(*plVar13 + 0x18))(plVar13);
        }
      }
    }
    break;
  default:
    plVar13 = (long *)param_2[1];
    if (plVar13 != (long *)0x0) {
      plVar1 = plVar13 + 1;
      do {
                    /* try { // try from 02bbe454 to 02cbe483 has its CatchHandler @ 02bbe490 */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_120 = local_b0;
    plStack_118 = local_a8;
    if (local_a8 != (long *)0x0) {
      plVar1 = local_a8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
              (param_1,extraout_x1,&local_120);
    if (plVar12 != (long *)0x0) {
      plVar1 = plVar12 + 1;
      do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbe454 with catch @ 02bbe490
                        */
        iVar11 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*plVar12 + 0x10))(plVar12);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
                    /* try { // try from 02bbe4c8 to 02cbe4f7 has its CatchHandler @ 02bbe504 */
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    if (plVar13 != (long *)0x0) {
      plVar12 = plVar13 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbe4c8 with catch @ 02bbe504
                        */
        (**(code **)(*plVar13 + 0x10))(plVar13);
                    /* catch() { ... } // from try @ 02bbe5d8 with catch @ 02bbe508
                       catch() { ... } // from try @ 02bbe7d8 with catch @ 02bbe508 */
        piVar10 = (int *)((long)plVar13 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar13 + 0x18))(plVar13);
        }
      }
    }
    break;
  case 4:
    plVar13 = (long *)param_2[1];
    if (plVar13 != (long *)0x0) {
      plVar1 = plVar13 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_f0 = local_b0;
    plStack_e8 = local_a8;
    if (local_a8 != (long *)0x0) {
      plVar1 = local_a8 + 1;
      do {
                    /* try { // try from 02bbe180 to 02cbe1af has its CatchHandler @ 02bbe23c */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
              (param_1,extraout_x1,&local_f0);
    if (plVar12 != (long *)0x0) {
      plVar1 = plVar12 + 1;
      do {
        iVar11 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*plVar12 + 0x10))(plVar12);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
                    /* try { // try from 02bbe1d8 to 02cbe207 has its CatchHandler @ 02bbe238 */
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    if (plVar13 != (long *)0x0) {
      plVar12 = plVar13 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
                    /* try { // try from 02bbe208 to 02cbe283 has its CatchHandler @ 02bbdd9c */
        (**(code **)(*plVar13 + 0x10))(plVar13);
        piVar10 = (int *)((long)plVar13 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
                    /* catch() { ... } // from try @ 02bbe1d8 with catch @ 02bbe238 */
                    /* catch() { ... } // from try @ 02bbe180 with catch @ 02bbe23c */
          (**(code **)(*plVar13 + 0x18))(plVar13);
                    /* catch() { ... } // from try @ 02bbe068 with catch @ 02bbe240 */
        }
      }
    }
    break;
  case 5:
    local_100 = *param_2;
    local_f8 = (long *)param_2[1];
    if (local_f8 != (long *)0x0) {
      plVar13 = local_f8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = (int)*plVar13 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_110 = local_b0;
    plStack_108 = local_a8;
    if (local_a8 != (long *)0x0) {
                    /* try { // try from 02bbe36c to 02cbe39b has its CatchHandler @ 02bbe3a8 */
      plVar13 = local_a8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = (int)*plVar13 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
              (param_1,&local_100,&local_110);
    if (plVar12 != (long *)0x0) {
      plVar13 = plVar12 + 1;
      do {
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbe36c with catch @ 02bbe3a8
                        */
      if (iVar11 == 0) {
        (**(code **)(*plVar12 + 0x10))(plVar12);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
                    /* try { // try from 02bbe3e0 to 02cbe40f has its CatchHandler @ 02bbe41c */
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
    plVar12 = local_f8;
    if (local_f8 != (long *)0x0) {
      plVar13 = local_f8 + 1;
      do {
        iVar11 = (int)*plVar13 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar3) {
          *(int *)plVar13 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 == 0) {
        (**(code **)(*local_f8 + 0x10))(local_f8);
        piVar10 = (int *)((long)plVar12 + 0xc);
        do {
          iVar11 = *piVar10;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbe3e0 with catch @ 02bbe41c
                        */
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*plVar12 + 0x18))(plVar12);
        }
      }
    }
  }
  plVar12 = (long *)*local_b0;
  if (local_b0 == plVar12) {
    if (local_a8 != (long *)0x0) {
      plVar12 = local_a8 + 1;
      do {
        iVar11 = (int)*plVar12 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
        if (bVar3) {
          *(int *)plVar12 = iVar11;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
                    /* try { // try from 02bbe6f0 to 02cbe71f has its CatchHandler @ 02bbe7e4 */
      if (iVar11 == 0) {
        (**(code **)(*local_a8 + 0x10))(local_a8);
        piVar10 = (int *)((long)local_a8 + 0xc);
        do {
          iVar11 = *piVar10;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
          if (bVar3) {
            *piVar10 = iVar11 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar11 + -1 == 0) {
          (**(code **)(*local_a8 + 0x18))(local_a8);
        }
      }
    }
    if (*(long *)(lVar6 + 0x28) == local_48) {
                    /* try { // try from 02bbe74c to 02cbe77b has its CatchHandler @ 02bbe7e0 */
      return;
    }
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  do {
    plVar12 = (long *)*plVar12;
  } while (local_b0 != plVar12);
  uVar7 = _Znwm(8);
  FUN_0307a6fc(uVar7,"Request error - ",&local_58);
                    /* try { // try from 02bbe574 to 02cbe583 has its CatchHandler @ 02bbe604 */
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_130,uVar7);
  local_140 = _Znwm(0x48);
  plVar12 = &local_130;
  local_150 = local_130;
  local_148 = plStack_128;
  if (plStack_128 != (long *)0x0) {
    plStack_128 = plStack_128 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plStack_128,0x10);
      if (bVar3) {
        *(int *)plStack_128 = (int)*plStack_128 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
                    /* try { // try from 02bbe5a8 to 02cbe5d7 has its CatchHandler @ 02bbe600 */
  local_160 = local_b0;
  local_158 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar12 = local_a8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar12,0x10);
      if (bVar3) {
        *(int *)plVar12 = (int)*plVar12 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
                    /* try { // try from 02bbe5d8 to 02cbe63b has its CatchHandler @ 02bbe508 */
  _ZN5Sfs2X10Exceptions18SFSValidationErrorC2EN5boost10shared_ptrISsEENS3_ISt4listISsSaISsEEEE
            (plVar12,local_140,&local_150,&local_160);
  uStack_138 = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions18SFSValidationErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_140,local_140,(ulong)&local_140 | 8);
  plVar12 = local_158;
  if (local_158 != (long *)0x0) {
    plVar13 = local_158 + 1;
    do {
                    /* catch() { ... } // from try @ 02bbe5a8 with catch @ 02bbe600 */
                    /* catch() { ... } // from try @ 02bbe574 with catch @ 02bbe604 */
      iVar11 = (int)*plVar13 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
      if (bVar3) {
        *(int *)plVar13 = iVar11;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar11 == 0) {
      (**(code **)(*local_158 + 0x10))(local_158);
      piVar10 = (int *)((long)plVar12 + 0xc);
      do {
        iVar11 = *piVar10;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar3) {
          *piVar10 = iVar11 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 + -1 == 0) {
                    /* try { // try from 02bbe63c to 02cbe667 has its CatchHandler @ 02bbe7ec */
        (**(code **)(*plVar12 + 0x18))(plVar12);
      }
    }
  }
  plVar12 = local_148;
  if (local_148 != (long *)0x0) {
    plVar13 = local_148 + 1;
    do {
      iVar11 = (int)*plVar13 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar13,0x10);
      if (bVar3) {
        *(int *)plVar13 = iVar11;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar11 == 0) {
      (**(code **)(*local_148 + 0x10))(local_148);
      piVar10 = (int *)((long)plVar12 + 0xc);
      do {
        iVar11 = *piVar10;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar10,0x10);
        if (bVar3) {
          *piVar10 = iVar11 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar11 + -1 == 0) {
                    /* try { // try from 02bbe694 to 02cbe6c3 has its CatchHandler @ 02bbe7e8 */
        (**(code **)(*plVar12 + 0x18))(plVar12);
      }
    }
  }
  puVar8 = (undefined8 *)__cxa_allocate_exception(0x10);
  uVar7 = uStack_138;
  puVar8[1] = 0;
  uStack_138 = 0;
  puVar8[1] = uVar7;
  *puVar8 = local_140;
  local_140 = 0;
                    /* WARNING: Subroutine does not return */
  __cxa_throw(puVar8,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEEE_03bd18c8
              ,PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions18SFSValidationErrorEED2Ev_03bd87c0);
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 02bbf138
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ValidatePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (long param_1,undefined8 *param_2,undefined8 *param_3)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  bool bVar4;
  long lVar5;
  undefined *puVar6;
  undefined8 *puVar7;
  ulong uVar8;
  long lVar9;
  code *pcVar10;
  int *piVar11;
  int iVar12;
  undefined8 uVar13;
  undefined8 local_90;
  long *local_88;
  undefined8 local_80;
  long *local_78;
  long *local_70;
  long *local_68;
  undefined1 auStack_60 [8];
  undefined *local_58 [2];
  long local_48;
  
  lVar5 = tpidr_el0;
  local_48 = *(long *)(lVar5 + 0x28);
  if ((*(long **)(param_1 + 0x58) == (long *)0x0) ||
     (*(long *)(**(long **)(param_1 + 0x58) + -0x18) == 0)) {
    uVar13 = *param_3;
    FUN_0307a6fc(local_58,"Public message is empty!",auStack_60);
    puVar7 = (undefined8 *)_Znwm(0x18);
    *puVar7 = 0;
    puVar7[1] = 0;
    puVar6 = PTR_DAT_03c37adf_1_03bd0478;
    puVar7[2] = local_58[0];
    local_58[0] = puVar6 + 0x18;
    FUN_0303d178(puVar7,uVar13);
    if (local_58[0] + -0x18 != puVar6) {
      piVar11 = (int *)(local_58[0] + -8);
                    /* try { // try from 02bbf3cc to 02cbf3d7 has its CatchHandler @ 02bbefec */
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar12 = *piVar11;
        *piVar11 = iVar12 + -1;
      }
      else {
        do {
          iVar12 = *piVar11;
                    /* catch() { ... } // from try @ 02bbf39c with catch @ 02bbf3d4 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar11,0x10);
          if (bVar4) {
            *piVar11 = iVar12 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
      }
      if (iVar12 < 1) {
        _ZdlPv(local_58[0] + -0x18);
        lVar9 = *(long *)(param_1 + 0x38);
        goto joined_r0x02bbf428;
      }
    }
  }
  lVar9 = *(long *)(param_1 + 0x38);
joined_r0x02bbf428:
  if (lVar9 != 0) {
    _ZN5Sfs2X8SmartFox6MySelfEv(&local_70,*param_2);
    local_80 = *(undefined8 *)(param_1 + 0x38);
                    /* try { // try from 02bbf1ec to 02cbf1f3 has its CatchHandler @ 02bbf290 */
    pcVar10 = *(code **)(*local_70 + 0x90);
    local_78 = *(long **)(param_1 + 0x40);
    if (local_78 != (long *)0x0) {
      plVar1 = local_78 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
                    /* try { // try from 02bbf21c to 02cbf24b has its CatchHandler @ 02bbf288 */
    uVar8 = (*pcVar10)(local_70,&local_80);
    plVar1 = local_78;
    if (local_78 != (long *)0x0) {
      plVar2 = local_78 + 1;
      do {
        iVar12 = (int)*plVar2 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
        if (bVar4) {
          *(int *)plVar2 = iVar12;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar12 == 0) {
                    /* try { // try from 02bbf24c to 02cbf2bf has its CatchHandler @ 02bbefec */
        (**(code **)(*local_78 + 0x10))(local_78);
        piVar11 = (int *)((long)plVar1 + 0xc);
        do {
          iVar12 = *piVar11;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar11,0x10);
          if (bVar4) {
            *piVar11 = iVar12 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar12 + -1 == 0) {
          (**(code **)(*plVar1 + 0x18))(plVar1);
        }
      }
    }
    if (local_68 != (long *)0x0) {
      plVar1 = local_68 + 1;
      do {
                    /* catch() { ... } // from try @ 02bbf21c with catch @ 02bbf288 */
                    /* catch() { ... } // from try @ 02bbf0d0 with catch @ 02bbf28c */
        iVar12 = (int)*plVar1 + -1;
                    /* catch() { ... } // from try @ 02bbf1ec with catch @ 02bbf290 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = iVar12;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02bbf0a0 with catch @ 02bbf294 */
      } while (cVar3 != '\0');
      if (iVar12 == 0) {
        (**(code **)(*local_68 + 0x10))(local_68);
        piVar11 = (int *)((long)local_68 + 0xc);
        do {
          iVar12 = *piVar11;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar11,0x10);
          if (bVar4) {
            *piVar11 = iVar12 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02bbf2c0 to 02cbf2ef has its CatchHandler @ 02bbf2f4 */
        if (iVar12 + -1 == 0) {
          (**(code **)(*local_68 + 0x18))(local_68);
        }
      }
    }
    if ((uVar8 & 1) == 0) {
      uVar13 = *param_3;
      (**(code **)(**(long **)(param_1 + 0x38) + 8))(&local_90);
                    /* catch() { ... } // from try @ 02bbf2c0 with catch @ 02bbf2f4 */
                    /* catch() { ... } // from try @ 02bbf070 with catch @ 02bbf2f8 */
      FUN_00af3838(local_58,"You are not joined in the target Room: ",local_90);
      puVar7 = (undefined8 *)_Znwm(0x18);
      *puVar7 = 0;
      puVar7[1] = 0;
      puVar6 = PTR_DAT_03c37adf_1_03bd0478;
      puVar7[2] = local_58[0];
                    /* try { // try from 02bbf324 to 02cbf353 has its CatchHandler @ 02bbf358 */
      local_58[0] = puVar6 + 0x18;
      FUN_0303d178(puVar7,uVar13);
      plVar1 = local_88;
      if (local_58[0] + -0x18 != puVar6) {
        piVar11 = (int *)(local_58[0] + -8);
        if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
          iVar12 = *piVar11;
          *piVar11 = iVar12 + -1;
        }
        else {
          do {
            iVar12 = *piVar11;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar11,0x10);
            if (bVar4) {
              *piVar11 = iVar12 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
        }
        if (iVar12 < 1) {
          _ZdlPv(local_58[0] + -0x18);
          plVar1 = local_88;
        }
      }
      if (plVar1 != (long *)0x0) {
        plVar2 = plVar1 + 1;
        do {
          iVar12 = (int)*plVar2 + -1;
                    /* try { // try from 02bbf354 to 02cbf39b has its CatchHandler @ 02bbefec */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(plVar2,0x10);
          if (bVar4) {
            *(int *)plVar2 = iVar12;
            cVar3 = ExclusiveMonitorsStatus();
          }
                    /* catch() { ... } // from try @ 02bbf324 with catch @ 02bbf358 */
        } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02bbf060 with catch @ 02bbf35c */
        if (iVar12 == 0) {
          (**(code **)(*plVar1 + 0x10))(plVar1);
                    /* catch() { ... } // from try @ 02bbf114 with catch @ 02bbf370 */
          piVar11 = (int *)((long)plVar1 + 0xc);
          do {
            iVar12 = *piVar11;
            cVar3 = '\x01';
            bVar4 = (bool)ExclusiveMonitorPass(piVar11,0x10);
            if (bVar4) {
              *piVar11 = iVar12 + -1;
              cVar3 = ExclusiveMonitorsStatus();
            }
          } while (cVar3 != '\0');
          if (iVar12 + -1 == 0) {
            (**(code **)(*plVar1 + 0x18))(plVar1);
          }
        }
      }
    }
  }
                    /* try { // try from 02bbf39c to 02cbf3cb has its CatchHandler @ 02bbf3d4 */
  if (*(long *)(lVar5 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 02bbf670
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest22ValidatePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (long param_1,undefined8 param_2,undefined8 *param_3)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  undefined8 *puVar5;
  undefined *__ptr;
  long *plVar6;
  int *piVar7;
  int iVar8;
  undefined8 uVar9;
  undefined1 auStack_60 [8];
  undefined *local_58 [2];
  long local_48;
  
  lVar3 = tpidr_el0;
  local_48 = *(long *)(lVar3 + 0x28);
  if ((*(long **)(param_1 + 0x58) == (long *)0x0) ||
     (*(long *)(**(long **)(param_1 + 0x58) + -0x18) == 0)) {
    uVar9 = *param_3;
                    /* try { // try from 02bbf6b4 to 02cbf6e7 has its CatchHandler @ 02bbf6b4
                       catch() { ... } // from try @ 02bbf6b4 with catch @ 02bbf6b4
                       catch() { ... } // from try @ 02bbf760 with catch @ 02bbf6b4 */
    FUN_0307a6fc(local_58,"Private message is empty!",auStack_60);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
    puVar5[2] = local_58[0];
                    /* try { // try from 02bbf6e8 to 02cbf6f3 has its CatchHandler @ 02bbf748 */
    local_58[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar9);
    if (local_58[0] + -0x18 == puVar4) goto LAB_02bbf704;
    piVar7 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar8 = *piVar7;
      *piVar7 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar7;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar7,0x10);
        if (bVar2) {
          *piVar7 = iVar8 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    if (0 < iVar8) goto LAB_02bbf704;
    _ZdlPv(local_58[0] + -0x18);
                    /* try { // try from 02bbf7d0 to 02cbf827 has its CatchHandler @ 02bbf8dc */
    plVar6 = *(long **)(param_1 + 0xa8);
    if (plVar6 != (long *)0x0) goto LAB_02bbf70c;
LAB_02bbf7d8:
    uVar9 = *param_3;
    FUN_0307a6fc(local_58,"Invalid recipient id",auStack_60);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
    puVar5[2] = local_58[0];
    local_58[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar9);
    __ptr = local_58[0] + -0x18;
    if (__ptr == puVar4) goto LAB_02bbf82c;
                    /* try { // try from 02bbf858 to 02cbf85f has its CatchHandler @ 02bbf8d8 */
    piVar7 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
LAB_02bbf878:
      iVar8 = *piVar7;
                    /* try { // try from 02bbf880 to 02cbf887 has its CatchHandler @ 02bbf8d4 */
      *piVar7 = iVar8 + -1;
    }
    else {
      do {
        iVar8 = *piVar7;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar7,0x10);
        if (bVar2) {
          *piVar7 = iVar8 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
  }
  else {
LAB_02bbf704:
    plVar6 = *(long **)(param_1 + 0xa8);
                    /* try { // try from 02bbf708 to 02cbf713 has its CatchHandler @ 02bbf728 */
    if (plVar6 == (long *)0x0) goto LAB_02bbf7d8;
LAB_02bbf70c:
    if (-1 < *plVar6) goto LAB_02bbf82c;
    uVar9 = *param_3;
                    /* catch() { ... } // from try @ 02bbf708 with catch @ 02bbf728 */
    FUN_0307a6fc(local_58,"Invalid recipient id: " + *plVar6,auStack_60);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bbf73c to 02cbf73f has its CatchHandler @ 02bbf744 */
                    /* catch() { ... } // from try @ 02bbf73c with catch @ 02bbf744 */
                    /* catch() { ... } // from try @ 02bbf6e8 with catch @ 02bbf748 */
    puVar5[2] = local_58[0];
                    /* try { // try from 02bbf750 to 02cbf75f has its CatchHandler @ 02bbf768 */
    local_58[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar9);
                    /* try { // try from 02bbf760 to 02cbf76b has its CatchHandler @ 02bbf6b4 */
    __ptr = local_58[0] + -0x18;
                    /* catch() { ... } // from try @ 02bbf750 with catch @ 02bbf768 */
    if (__ptr == puVar4) goto LAB_02bbf82c;
                    /* catch() { ... } // from try @ 02bbf888 with catch @ 02bbf76c */
    piVar7 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) goto LAB_02bbf878;
    do {
      iVar8 = *piVar7;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(piVar7,0x10);
      if (bVar2) {
        *piVar7 = iVar8 + -1;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
  }
                    /* try { // try from 02bbf888 to 02cbf8df has its CatchHandler @ 02bbf76c */
  if (iVar8 < 1) {
    _ZdlPv(__ptr);
  }
LAB_02bbf82c:
  if (*(long *)(lVar3 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 02bbf9a0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ValidateObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (long param_1,undefined8 param_2,undefined8 *param_3)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  undefined8 *puVar5;
  int *piVar6;
  int iVar7;
  undefined8 uVar8;
  undefined1 auStack_50 [8];
  undefined *local_48 [2];
  long local_38;
  
                    /* try { // try from 02bbf9a0 to 02cbf9bf has its CatchHandler @ 02bbf9fc */
  lVar3 = tpidr_el0;
  local_38 = *(long *)(lVar3 + 0x28);
  if (*(long *)(param_1 + 0x68) == 0) {
    uVar8 = *param_3;
                    /* try { // try from 02bbf9cc to 02cbf9d3 has its CatchHandler @ 02bbfa0c */
                    /* try { // try from 02bbf9d4 to 02cbfa1b has its CatchHandler @ 02bbf8e0 */
    FUN_0307a6fc(local_48,"Object message is null!",auStack_50);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* catch() { ... } // from try @ 02bbf9a0 with catch @ 02bbf9fc */
    puVar5[2] = local_48[0];
    local_48[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar8);
                    /* catch() { ... } // from try @ 02bbf9cc with catch @ 02bbfa0c */
                    /* catch() { ... } // from try @ 02bbf984 with catch @ 02bbfa10 */
    if (local_48[0] + -0x18 != puVar4) {
                    /* catch() { ... } // from try @ 02bbfa28 with catch @ 02bbfa40 */
                    /* catch() { ... } // from try @ 02bbfa1c with catch @ 02bbfa44 */
                    /* catch() { ... } // from try @ 02bbf97c with catch @ 02bbfa48 */
      piVar6 = (int *)(local_48[0] + -8);
                    /* catch() { ... } // from try @ 02bbf938 with catch @ 02bbfa4c */
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar7 = *piVar6;
        *piVar6 = iVar7 + -1;
      }
      else {
        do {
                    /* try { // try from 02bbfa50 to 02cbfabf has its CatchHandler @ 02bbfa50
                       catch() { ... } // from try @ 02bbfa50 with catch @ 02bbfa50
                       catch() { ... } // from try @ 02bbfb10 with catch @ 02bbfa50
                       catch() { ... } // from try @ 02bbfb50 with catch @ 02bbfa50 */
          iVar7 = *piVar6;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar2) {
            *piVar6 = iVar7 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar7 < 1) {
        _ZdlPv(local_48[0] + -0x18);
      }
    }
  }
                    /* try { // try from 02bbfa1c to 02cbfa23 has its CatchHandler @ 02bbfa44 */
                    /* try { // try from 02bbfa28 to 02cbfa37 has its CatchHandler @ 02bbfa40 */
  if (*(long *)(lVar3 + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02bbfa38 to 02cbfa4f has its CatchHandler @ 02bbf8e0 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 02bbfafc
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ValidateBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (long param_1,undefined8 *param_2,undefined8 *param_3)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  ulong uVar5;
  undefined8 *puVar6;
  long *plVar7;
  int *piVar8;
  int iVar9;
  undefined8 uVar10;
  long *local_80;
  long *local_78;
  undefined1 auStack_70 [8];
  undefined *local_68;
  undefined8 *local_60;
  long *local_58;
  long local_48;
  
                    /* try { // try from 02bbfb08 to 02cbfb0f has its CatchHandler @ 02bbfb38 */
                    /* try { // try from 02bbfb10 to 02cbfb47 has its CatchHandler @ 02bbfa50 */
  lVar3 = tpidr_el0;
  local_48 = *(long *)(lVar3 + 0x28);
                    /* catch() { ... } // from try @ 02bbfb08 with catch @ 02bbfb38 */
  _ZN5Sfs2X8SmartFox12BuddyManagerEv(&local_60,*param_2);
                    /* catch() { ... } // from try @ 02bbfaf4 with catch @ 02bbfb3c */
                    /* try { // try from 02bbfb48 to 02cbfb4f has its CatchHandler @ 02bbfb58 */
  uVar5 = (**(code **)*local_60)();
                    /* try { // try from 02bbfb50 to 02cbfb63 has its CatchHandler @ 02bbfa50 */
  if (local_58 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bbfb48 with catch @ 02bbfb58 */
    plVar7 = local_58 + 1;
    do {
                    /* catch() { ... } // from try @ 02bbfaec with catch @ 02bbfb5c */
                    /* catch() { ... } // from try @ 02bbfac0 with catch @ 02bbfb60 */
      iVar9 = (int)*plVar7 + -1;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar7,0x10);
      if (bVar2) {
        *(int *)plVar7 = iVar9;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar8 = (int *)((long)local_58 + 0xc);
      do {
        iVar9 = *piVar8;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
        if (bVar2) {
          *piVar8 = iVar9 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_58 + 0x18))(local_58);
      }
    }
  }
  if ((uVar5 & 1) == 0) {
                    /* try { // try from 02bbfbac to 02cbfc83 has its CatchHandler @ 02bbfbac
                       catch() { ... } // from try @ 02bbfbac with catch @ 02bbfbac
                       catch() { ... } // from try @ 02bbfca4 with catch @ 02bbfbac
                       catch() { ... } // from try @ 02bbfcec with catch @ 02bbfbac */
    uVar10 = *param_3;
    FUN_0307a6fc(&local_68,"BuddyList is not inited. Please send an InitBuddyRequest first.",
                 auStack_70);
    puVar6 = (undefined8 *)_Znwm(0x18);
    *puVar6 = 0;
    puVar6[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
    puVar6[2] = local_68;
    local_68 = puVar4 + 0x18;
    FUN_0303d178(puVar6,uVar10);
    if (local_68 + -0x18 != puVar4) {
                    /* try { // try from 02bbfde8 to 02cbfe23 has its CatchHandler @ 02bbfd18 */
      piVar8 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar9 = *piVar8;
        *piVar8 = iVar9 + -1;
      }
      else {
        do {
          iVar9 = *piVar8;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
          if (bVar2) {
            *piVar8 = iVar9 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar9 < 1) {
        _ZdlPv(local_68 + -0x18);
      }
    }
  }
  _ZN5Sfs2X8SmartFox12BuddyManagerEv(&local_80,*param_2);
  uVar5 = (**(code **)(*local_80 + 0x90))();
  if (local_78 != (long *)0x0) {
    plVar7 = local_78 + 1;
    do {
      iVar9 = (int)*plVar7 + -1;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(plVar7,0x10);
      if (bVar2) {
        *(int *)plVar7 = iVar9;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
    if (iVar9 == 0) {
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar8 = (int *)((long)local_78 + 0xc);
      do {
        iVar9 = *piVar8;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
        if (bVar2) {
          *piVar8 = iVar9 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
      if (iVar9 + -1 == 0) {
        (**(code **)(*local_78 + 0x18))(local_78);
      }
    }
  }
  if ((uVar5 & 1) == 0) {
    uVar10 = *param_3;
                    /* try { // try from 02bbfc84 to 02cbfc8f has its CatchHandler @ 02bbfcd0 */
    FUN_0307a6fc(&local_68,"Can\'t send messages while off-line",auStack_70);
    puVar6 = (undefined8 *)_Znwm(0x18);
                    /* try { // try from 02bbfc9c to 02cbfca3 has its CatchHandler @ 02bbfccc */
    *puVar6 = 0;
    puVar6[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bbfca4 to 02cbfcdf has its CatchHandler @ 02bbfbac */
    puVar6[2] = local_68;
    local_68 = puVar4 + 0x18;
    FUN_0303d178(puVar6,uVar10);
                    /* catch() { ... } // from try @ 02bbfc9c with catch @ 02bbfccc */
    if (local_68 + -0x18 != puVar4) {
      piVar8 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar9 = *piVar8;
        *piVar8 = iVar9 + -1;
      }
      else {
        do {
          iVar9 = *piVar8;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfde0 with catch @ 02bbfe20
                        */
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
          if (bVar2) {
            *piVar8 = iVar9 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfe44 with catch @ 02bbfe24
                       catch(type#1 @ 00000000) { ... } // from try @ 02bbfea8 with catch @ 02bbfe24
                        */
        } while (cVar1 != '\0');
      }
                    /* try { // try from 02bbfe9c to 02cbfe9f has its CatchHandler @ 02bbfea0 */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfe9c with catch @ 02bbfea0
                        */
      if (iVar9 < 1) {
                    /* try { // try from 02bbfea4 to 02cbfea7 has its CatchHandler @ 02bbfeb0 */
                    /* try { // try from 02bbfea8 to 02cbfeb3 has its CatchHandler @ 02bbfe24 */
        _ZdlPv(local_68 + -0x18);
        plVar7 = *(long **)(param_1 + 0x58);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfea4 with catch @ 02bbfeb0
                        */
        goto joined_r0x02bbfcd4;
      }
    }
  }
                    /* catch() { ... } // from try @ 02bbfc84 with catch @ 02bbfcd0 */
  plVar7 = *(long **)(param_1 + 0x58);
joined_r0x02bbfcd4:
                    /* try { // try from 02bbfce0 to 02cbfceb has its CatchHandler @ 02bbfcf4 */
  if ((plVar7 == (long *)0x0) || (*(long *)(*plVar7 + -0x18) == 0)) {
    uVar10 = *param_3;
                    /* try { // try from 02bbfcec to 02cbfcf7 has its CatchHandler @ 02bbfbac */
                    /* catch() { ... } // from try @ 02bbfce0 with catch @ 02bbfcf4 */
    FUN_0307a6fc(&local_68,"Buddy message is empty!",auStack_70);
    puVar6 = (undefined8 *)_Znwm(0x18);
    *puVar6 = 0;
    puVar6[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfd98 with catch @ 02bbfd18
                       catch(type#1 @ 00000000) { ... } // from try @ 02bbfde8 with catch @ 02bbfd18
                        */
    puVar6[2] = local_68;
    local_68 = puVar4 + 0x18;
    FUN_0303d178(puVar6,uVar10);
    if (local_68 + -0x18 != puVar4) {
      piVar8 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar9 = *piVar8;
        *piVar8 = iVar9 + -1;
      }
      else {
        do {
          iVar9 = *piVar8;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfd8c with catch @ 02bbfdd4
                        */
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfd68 with catch @ 02bbfdd8
                        */
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
          if (bVar2) {
            *piVar8 = iVar9 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar9 < 1) {
        _ZdlPv(local_68 + -0x18);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bbfe3c with catch @ 02bbfe6c
                        */
      }
    }
  }
  if (**(long **)(param_1 + 0xa8) < 0) {
    uVar10 = *param_3;
    FUN_0307a6fc(&local_68,"Recipient is not online or not in your buddy list",auStack_70);
    puVar6 = (undefined8 *)_Znwm(0x18);
    *puVar6 = 0;
    puVar6[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bbfd68 to 02cbfd6b has its CatchHandler @ 02bbfdd8 */
    puVar6[2] = local_68;
    local_68 = puVar4 + 0x18;
    FUN_0303d178(puVar6,uVar10);
                    /* try { // try from 02bbfd8c to 02cbfd97 has its CatchHandler @ 02bbfdd4 */
    if (local_68 + -0x18 != puVar4) {
      piVar8 = (int *)(local_68 + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar9 = *piVar8;
        *piVar8 = iVar9 + -1;
      }
      else {
        do {
                    /* try { // try from 02bbfe3c to 02cbfe43 has its CatchHandler @ 02bbfe6c */
          iVar9 = *piVar8;
                    /* try { // try from 02bbfe44 to 02cbfe9b has its CatchHandler @ 02bbfe24 */
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar8,0x10);
          if (bVar2) {
            *piVar8 = iVar9 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar9 < 1) {
        _ZdlPv(local_68 + -0x18);
      }
    }
  }
                    /* try { // try from 02bbfd98 to 02cbfddf has its CatchHandler @ 02bbfd18 */
  if (*(long *)(lVar3 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
// ADDRESS : 02bc00f0
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest24ValidateSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEENS3_ISt4listISsSaISsEEEE
               (long param_1,undefined8 param_2,undefined8 *param_3)

{
  char cVar1;
  bool bVar2;
  long lVar3;
  undefined *puVar4;
  undefined8 *puVar5;
  undefined *__ptr;
  int *piVar6;
  int iVar7;
  undefined8 uVar8;
  undefined1 auStack_60 [8];
  undefined *local_58 [2];
  long local_48;
  
                    /* catch() { ... } // from try @ 02bc0190 with catch @ 02bc00f8
                       catch() { ... } // from try @ 02bc01d4 with catch @ 02bc00f8 */
  lVar3 = tpidr_el0;
  local_48 = *(long *)(lVar3 + 0x28);
                    /* try { // try from 02bc0114 to 02cc011b has its CatchHandler @ 02bc01b0 */
  if ((*(long **)(param_1 + 0x58) == (long *)0x0) ||
     (*(long *)(**(long **)(param_1 + 0x58) + -0x18) == 0)) {
    uVar8 = *param_3;
    FUN_0307a6fc(local_58,"Moderator message is empty!",auStack_60);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bc0160 to 02cc018f has its CatchHandler @ 02bc01ac */
    puVar5[2] = local_58[0];
    local_58[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar8);
    if (local_58[0] + -0x18 != puVar4) {
      piVar6 = (int *)(local_58[0] + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
        iVar7 = *piVar6;
        *piVar6 = iVar7 + -1;
      }
      else {
        do {
          iVar7 = *piVar6;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar2) {
            *piVar6 = iVar7 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
        } while (cVar1 != '\0');
      }
      if (iVar7 < 1) {
        _ZdlPv(local_58[0] + -0x18);
      }
    }
  }
  iVar7 = *(int *)(param_1 + 200);
  if (iVar7 == 2) {
    if (*(long *)(param_1 + 0x98) != 0) goto LAB_02bc02f8;
    uVar8 = *param_3;
    FUN_0307a6fc(local_58,"TO_GROUP expects a String object (the groupId) as recipient",auStack_60);
    puVar5 = (undefined8 *)_Znwm(0x18);
    *puVar5 = 0;
    puVar5[1] = 0;
    puVar4 = PTR_DAT_03c37adf_1_03bd0478;
    puVar5[2] = local_58[0];
    local_58[0] = puVar4 + 0x18;
    FUN_0303d178(puVar5,uVar8);
    __ptr = local_58[0] + -0x18;
    if (__ptr == puVar4) goto LAB_02bc02f8;
    piVar6 = (int *)(local_58[0] + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) goto LAB_02bc0388;
    do {
      iVar7 = *piVar6;
      cVar1 = '\x01';
      bVar2 = (bool)ExclusiveMonitorPass(piVar6,0x10);
      if (bVar2) {
        *piVar6 = iVar7 + -1;
        cVar1 = ExclusiveMonitorsStatus();
      }
    } while (cVar1 != '\0');
  }
  else {
                    /* try { // try from 02bc0190 to 02cc01c7 has its CatchHandler @ 02bc00f8 */
    if (iVar7 == 1) {
      if (*(long *)(param_1 + 0x88) != 0) goto LAB_02bc02f8;
      uVar8 = *param_3;
      FUN_0307a6fc(local_58,"TO_ROOM expects a Room object as recipient",auStack_60);
      puVar5 = (undefined8 *)_Znwm(0x18);
      *puVar5 = 0;
      puVar5[1] = 0;
      puVar4 = PTR_DAT_03c37adf_1_03bd0478;
      puVar5[2] = local_58[0];
      local_58[0] = puVar4 + 0x18;
      FUN_0303d178(puVar5,uVar8);
      __ptr = local_58[0] + -0x18;
      if (__ptr == puVar4) goto LAB_02bc02f8;
                    /* try { // try from 02bc0278 to 02cc027f has its CatchHandler @ 02bc0300 */
                    /* try { // try from 02bc0280 to 02cc0313 has its CatchHandler @ 02bc0214 */
      piVar6 = (int *)(local_58[0] + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) goto LAB_02bc0388;
      do {
        iVar7 = *piVar6;
        cVar1 = '\x01';
        bVar2 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar2) {
          *piVar6 = iVar7 + -1;
          cVar1 = ExclusiveMonitorsStatus();
        }
      } while (cVar1 != '\0');
    }
    else {
      if ((iVar7 != 0) || (*(long *)(param_1 + 0x78) != 0)) goto LAB_02bc02f8;
      uVar8 = *param_3;
                    /* catch() { ... } // from try @ 02bc0160 with catch @ 02bc01ac */
                    /* catch() { ... } // from try @ 02bc0114 with catch @ 02bc01b0 */
      FUN_0307a6fc(local_58,"TO_USER expects a User object as recipient",auStack_60);
      puVar5 = (undefined8 *)_Znwm(0x18);
      *puVar5 = 0;
      puVar5[1] = 0;
      puVar4 = PTR_DAT_03c37adf_1_03bd0478;
                    /* try { // try from 02bc01c8 to 02cc01cb has its CatchHandler @ 02bc01cc */
                    /* catch() { ... } // from try @ 02bc01c8 with catch @ 02bc01cc */
                    /* try { // try from 02bc01d0 to 02cc01d3 has its CatchHandler @ 02bc01dc */
                    /* try { // try from 02bc01d4 to 02cc01df has its CatchHandler @ 02bc00f8 */
      puVar5[2] = local_58[0];
                    /* catch() { ... } // from try @ 02bc01d0 with catch @ 02bc01dc */
      local_58[0] = puVar4 + 0x18;
      FUN_0303d178(puVar5,uVar8);
      __ptr = local_58[0] + -0x18;
      if (__ptr == puVar4) goto LAB_02bc02f8;
      piVar6 = (int *)(local_58[0] + -8);
      if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
LAB_02bc0388:
        iVar7 = *piVar6;
        *piVar6 = iVar7 + -1;
      }
      else {
        do {
          iVar7 = *piVar6;
          cVar1 = '\x01';
          bVar2 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar2) {
            *piVar6 = iVar7 + -1;
            cVar1 = ExclusiveMonitorsStatus();
          }
                    /* try { // try from 02bc0214 to 02cc0277 has its CatchHandler @ 02bc0214
                       catch() { ... } // from try @ 02bc0214 with catch @ 02bc0214
                       catch() { ... } // from try @ 02bc0280 with catch @ 02bc0214 */
        } while (cVar1 != '\0');
      }
    }
  }
                    /* try { // try from 02bc0398 to 02cc03ab has its CatchHandler @ 02bc04b8 */
  if (iVar7 < 1) {
    _ZdlPv(__ptr);
  }
LAB_02bc02f8:
                    /* catch() { ... } // from try @ 02bc0278 with catch @ 02bc0300 */
  if (*(long *)(lVar3 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02bc0314 to 02cc0397 has its CatchHandler @ 02bc0314
                       catch() { ... } // from try @ 02bc0314 with catch @ 02bc0314
                       catch() { ... } // from try @ 02bc0454 with catch @ 02bc0314 */
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc04f4
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest7ExecuteEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  code *pcVar8;
  undefined8 local_88;
  long *plStack_80;
  undefined8 local_78;
  long *plStack_70;
  undefined1 *local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  undefined1 *local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  local_48 = (undefined1 *)_Znwm(1);
  *local_48 = 0;
  local_40 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIhhEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_48,local_48,&local_40);
  *local_48 = (char)*(undefined8 *)(param_1 + 0x30);
  plVar7 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar7 + 0x1e8);
  local_58 = *(undefined8 *)
              PTR__ZN5Sfs2X8Requests21GenericMessageRequest16KEY_MESSAGE_TYPEE_03bd3d58;
  local_50 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest16KEY_MESSAGE_TYPEE_03bd3d58 +
                       8);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02bc0580 to 02cc058b has its CatchHandler @ 02bc05bc */
    } while (cVar3 != '\0');
  }
  local_68 = local_48;
  local_60 = local_40;
                    /* try { // try from 02bc058c to 02cc065f has its CatchHandler @ 02bc04cc */
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar8)(plVar7,&local_58,&local_68);
  plVar7 = local_60;
  if (local_60 != (long *)0x0) {
    plVar1 = local_60 + 1;
    do {
                    /* catch() { ... } // from try @ 02bc0580 with catch @ 02bc05bc */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_50;
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
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
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
                    /* try { // try from 02bc0660 to 02cc0663 has its CatchHandler @ 02bc0690 */
                    /* try { // try from 02bc0664 to 02cc06a3 has its CatchHandler @ 02bc04cc */
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    local_78 = *param_2;
    plVar7 = (long *)param_2[1];
    if (plVar7 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bc0660 with catch @ 02bc0690 */
      plVar1 = plVar7 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
                    /* try { // try from 02bc06a4 to 02cc0777 has its CatchHandler @ 02bc06a4
                       catch() { ... } // from try @ 02bc06a4 with catch @ 02bc06a4
                       catch() { ... } // from try @ 02bc0800 with catch @ 02bc06a4
                       catch() { ... } // from try @ 02bc087c with catch @ 02bc06a4 */
    plStack_70 = plVar7;
    _ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE
              (param_1,&local_78);
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
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
        (**(code **)(*plVar7 + 0x10))(plVar7);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    break;
  case 1:
    plVar7 = (long *)param_2[1];
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE
              (param_1);
    if (plVar7 != (long *)0x0) {
                    /* try { // try from 02bc07b8 to 02cc07ff has its CatchHandler @ 02bc0894 */
      plVar1 = plVar7 + 1;
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
        (**(code **)(*plVar7 + 0x10))(plVar7);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* try { // try from 02bc0800 to 02cc0873 has its CatchHandler @ 02bc06a4 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    break;
  default:
    plVar7 = (long *)param_2[1];
    if (plVar7 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bc0778 with catch @ 02bc0890 */
      plVar1 = plVar7 + 1;
      do {
                    /* catch() { ... } // from try @ 02bc07b8 with catch @ 02bc0894 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE
              (param_1);
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
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
        (**(code **)(*plVar7 + 0x10))(plVar7);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* catch() { ... } // from try @ 02bc09b0 with catch @ 02bc08fc */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    break;
  case 4:
    local_88 = *param_2;
    plVar7 = (long *)param_2[1];
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    plStack_80 = plVar7;
    _ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE
              (param_1,&local_88);
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
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
        (**(code **)(*plVar7 + 0x10))(plVar7);
        piVar2 = (int *)((long)plVar7 + 0xc);
        do {
          iVar5 = *piVar2;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02bc0778 to 02cc078b has its CatchHandler @ 02bc0890 */
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    break;
  case 5:
    plVar7 = (long *)param_2[1];
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    _ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE
              (param_1);
    if (plVar7 != (long *)0x0) {
      plVar1 = plVar7 + 1;
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
        (**(code **)(*plVar7 + 0x10))(plVar7);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* try { // try from 02bc0874 to 02cc087b has its CatchHandler @ 02bc087c */
                    /* catch() { ... } // from try @ 02bc0874 with catch @ 02bc087c
                       try { // try from 02bc087c to 02cc08fb has its CatchHandler @ 02bc06a4 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  plVar7 = local_40;
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc0d04
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ExecutePublicMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  char cVar2;
  bool bVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  undefined8 *puVar8;
  code *pcVar9;
  long lVar10;
  long *plVar11;
  long local_130;
  long *local_128;
  undefined8 local_120;
  long *local_118;
  undefined8 local_110;
  long *local_108;
  undefined8 local_100;
  long *local_f8;
  undefined8 *local_f0;
  long *local_e8;
  undefined8 local_e0;
  long *local_d8;
  undefined8 *local_d0;
  long *local_c8;
  undefined8 *local_c0;
  long *local_b8;
  undefined8 *local_b0;
  long *local_a8;
  undefined8 local_a0;
  long *local_98;
  undefined8 *local_90;
  long *local_88;
  undefined8 local_80;
  long *local_78;
  undefined8 local_70;
  undefined8 uStack_68;
  undefined8 local_58;
  long *local_50;
  long local_48;
  
  lVar5 = tpidr_el0;
  local_48 = *(long *)(lVar5 + 0x28);
  if (*(long *)(param_1 + 0x38) == 0) {
    _ZN5Sfs2X8SmartFox14LastJoinedRoomEv(&local_58,*param_2);
    plVar7 = local_50;
    uVar6 = local_58;
    local_58 = 0;
    local_50 = (long *)0x0;
    plVar11 = *(long **)(param_1 + 0x40);
    *(undefined8 *)(param_1 + 0x38) = uVar6;
    *(long **)(param_1 + 0x40) = plVar7;
    if (plVar11 != (long *)0x0) {
      plVar7 = plVar11 + 1;
      do {
        iVar4 = (int)*plVar7 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar7,0x10);
        if (bVar3) {
          *(int *)plVar7 = iVar4;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 == 0) {
        (**(code **)(*plVar11 + 0x10))(plVar11);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar4 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar4 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar4 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    plVar7 = local_50;
    if (local_50 != (long *)0x0) {
      plVar11 = local_50 + 1;
      do {
        iVar4 = (int)*plVar11 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar3) {
          *(int *)plVar11 = iVar4;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 == 0) {
        (**(code **)(*local_50 + 0x10))(local_50);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar4 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar4 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar4 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    if (*(long *)(param_1 + 0x38) == 0) {
      uVar6 = _Znwm(8);
      FUN_0307a6fc(uVar6,"User should be joined in a room in order to send a public message",
                   &local_70);
      _ZN5boost10shared_ptrISsEC2ISsEEPT_(&local_58,uVar6);
      local_70 = _Znwm(0x38);
      local_80 = local_58;
      local_78 = local_50;
      if (local_50 != (long *)0x0) {
        plVar7 = local_50 + 1;
        do {
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar7,0x10);
          if (bVar3) {
            *(int *)plVar7 = (int)*plVar7 + 1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
      }
      _ZN5Sfs2X10Exceptions8SFSErrorC1EN5boost10shared_ptrISsEE(local_70,&local_80);
      uStack_68 = 0;
      _ZN5boost6detail20sp_pointer_constructIN5Sfs2X10Exceptions8SFSErrorES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
                (&local_70,local_70,(ulong)&local_70 | 8);
      plVar7 = local_78;
      if (local_78 != (long *)0x0) {
        plVar11 = local_78 + 1;
        do {
          iVar4 = (int)*plVar11 + -1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
          if (bVar3) {
            *(int *)plVar11 = iVar4;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar4 == 0) {
          (**(code **)(*local_78 + 0x10))(local_78);
          piVar1 = (int *)((long)plVar7 + 0xc);
          do {
            iVar4 = *piVar1;
            cVar2 = '\x01';
            bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
            if (bVar3) {
              *piVar1 = iVar4 + -1;
              cVar2 = ExclusiveMonitorsStatus();
            }
          } while (cVar2 != '\0');
          if (iVar4 + -1 == 0) {
            (**(code **)(*plVar7 + 0x18))(plVar7);
          }
        }
      }
      puVar8 = (undefined8 *)__cxa_allocate_exception(0x10);
      uVar6 = uStack_68;
      puVar8[1] = 0;
      uStack_68 = 0;
      puVar8[1] = uVar6;
      *puVar8 = local_70;
      local_70 = 0;
                    /* WARNING: Subroutine does not return */
      __cxa_throw(puVar8,PTR__ZTIN5boost10shared_ptrIN5Sfs2X10Exceptions8SFSErrorEEE_03bd5a38,
                  PTR__ZN5boost10shared_ptrIN5Sfs2X10Exceptions8SFSErrorEED2Ev_03bd4130);
    }
  }
  local_90 = (undefined8 *)_Znwm(8);
  *local_90 = 0;
  local_88 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_90,local_90,&local_88);
  uVar6 = (**(code **)**(undefined8 **)(param_1 + 0x38))();
  *local_90 = uVar6;
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x228);
  local_a0 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_ROOM_IDE_03bd0e30;
  local_98 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_ROOM_IDE_03bd0e30 + 8);
  if (local_98 != (long *)0x0) {
    plVar11 = local_98 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_b0 = local_90;
  local_a8 = local_88;
  if (local_88 != (long *)0x0) {
    plVar11 = local_88 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar9)(plVar7,&local_a0,&local_b0);
  plVar7 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar11 = local_a8 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_98;
  if (local_98 != (long *)0x0) {
    plVar11 = local_98 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  local_c0 = (undefined8 *)_Znwm(8);
  *local_c0 = 0;
  local_b8 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_c0,local_c0,&local_b8);
  _ZN5Sfs2X8SmartFox6MySelfEv(&local_d0,*param_2);
  uVar6 = (**(code **)*local_d0)();
  *local_c0 = uVar6;
  if (local_c8 != (long *)0x0) {
    plVar7 = local_c8 + 1;
    do {
      iVar4 = (int)*plVar7 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar7,0x10);
      if (bVar3) {
        *(int *)plVar7 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar1 = (int *)((long)local_c8 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*local_c8 + 0x18))(local_c8);
      }
    }
  }
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x228);
  local_e0 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_USER_IDE_03bd2118;
  local_d8 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_USER_IDE_03bd2118 + 8);
  if (local_d8 != (long *)0x0) {
    plVar11 = local_d8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_f0 = local_c0;
  local_e8 = local_b8;
  if (local_b8 != (long *)0x0) {
    plVar11 = local_b8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar9)(plVar7,&local_e0,&local_f0);
  plVar7 = local_e8;
  if (local_e8 != (long *)0x0) {
    plVar11 = local_e8 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_e8 + 0x10))(local_e8);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_d8;
  if (local_d8 != (long *)0x0) {
    plVar11 = local_d8 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_d8 + 0x10))(local_d8);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x2a8);
  local_100 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88;
  local_f8 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88 + 8);
  if (local_f8 != (long *)0x0) {
    plVar11 = local_f8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  local_110 = *(undefined8 *)(param_1 + 0x58);
  local_108 = *(long **)(param_1 + 0x60);
  if (local_108 != (long *)0x0) {
    plVar11 = local_108 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = (int)*plVar11 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar9)(plVar7,&local_100,&local_110);
  plVar7 = local_108;
  if (local_108 != (long *)0x0) {
    plVar11 = local_108 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
                    /* catch() { ... } // from try @ 02bc1204 with catch @ 02bc11a4
                       catch() { ... } // from try @ 02bc1628 with catch @ 02bc11a4
                       catch() { ... } // from try @ 02bc1778 with catch @ 02bc11a4 */
      (**(code **)(*local_108 + 0x10))(local_108);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_f8;
  if (local_f8 != (long *)0x0) {
    plVar11 = local_f8 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
                    /* try { // try from 02bc11f8 to 02cc1203 has its CatchHandler @ 02bc1864 */
      (**(code **)(*local_f8 + 0x10))(local_f8);
                    /* try { // try from 02bc1204 to 02cc1603 has its CatchHandler @ 02bc11a4 */
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  lVar10 = *(long *)(param_1 + 0x68);
  if (lVar10 != 0) {
    plVar7 = *(long **)(param_1 + 8);
    pcVar9 = *(code **)(*plVar7 + 0x378);
    local_120 = *(undefined8 *)
                 PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38;
    local_118 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38
                          + 8);
    if (local_118 != (long *)0x0) {
      plVar11 = local_118 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar3) {
          *(int *)plVar11 = (int)*plVar11 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      lVar10 = *(long *)(param_1 + 0x68);
    }
    local_128 = *(long **)(param_1 + 0x70);
    if (local_128 != (long *)0x0) {
      plVar11 = local_128 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar3) {
          *(int *)plVar11 = (int)*plVar11 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    local_130 = lVar10;
    (*pcVar9)(plVar7,&local_120,&local_130);
    plVar7 = local_128;
    if (local_128 != (long *)0x0) {
      plVar11 = local_128 + 1;
      do {
        iVar4 = (int)*plVar11 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar3) {
          *(int *)plVar11 = iVar4;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 == 0) {
        (**(code **)(*local_128 + 0x10))(local_128);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar4 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar4 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar4 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_118;
    if (local_118 != (long *)0x0) {
      plVar11 = local_118 + 1;
      do {
        iVar4 = (int)*plVar11 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar3) {
          *(int *)plVar11 = iVar4;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 == 0) {
        (**(code **)(*local_118 + 0x10))(local_118);
        piVar1 = (int *)((long)plVar7 + 0xc);
        do {
          iVar4 = *piVar1;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar3) {
            *piVar1 = iVar4 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar4 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  plVar7 = local_b8;
  if (local_b8 != (long *)0x0) {
    plVar11 = local_b8 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_b8 + 0x10))(local_b8);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_88;
  if (local_88 != (long *)0x0) {
    plVar11 = local_88 + 1;
    do {
      iVar4 = (int)*plVar11 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar11,0x10);
      if (bVar3) {
        *(int *)plVar11 = iVar4;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar4 == 0) {
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar1 = (int *)((long)plVar7 + 0xc);
      do {
        iVar4 = *piVar1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar3) {
          *piVar1 = iVar4 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar4 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  if (*(long *)(lVar5 + 0x28) == local_48) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc1c4c
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest21ExecutePrivateMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  code *pcVar8;
  long lVar9;
  long local_98;
  long *local_90;
  undefined8 local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  undefined8 local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  plVar7 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar7 + 0x228);
  local_48 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0;
  local_40 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 + 8);
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_58 = *(undefined8 *)(param_1 + 0xa8);
  local_50 = *(long **)(param_1 + 0xb0);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar8)(plVar7,&local_48,&local_58);
  plVar7 = local_50;
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
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
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_40;
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar7 + 0x2a8);
  local_68 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88;
  local_60 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88 + 8);
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
  local_78 = *(undefined8 *)(param_1 + 0x58);
  local_70 = *(long **)(param_1 + 0x60);
  if (local_70 != (long *)0x0) {
    plVar1 = local_70 + 1;
    do {
                    /* catch() { ... } // from try @ 02bc1ae8 with catch @ 02bc1dd8 */
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar8)(plVar7,&local_68,&local_78);
  plVar7 = local_70;
  if (local_70 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_60;
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
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)plVar7 + 0xc);
      do {
                    /* catch() { ... } // from try @ 02bc1bb0 with catch @ 02bc1e7c */
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  lVar9 = *(long *)(param_1 + 0x68);
  if (lVar9 != 0) {
    plVar7 = *(long **)(param_1 + 8);
    pcVar8 = *(code **)(*plVar7 + 0x378);
    local_88 = *(undefined8 *)
                PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38;
    local_80 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38 +
                         8);
    if (local_80 != (long *)0x0) {
      plVar1 = local_80 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      lVar9 = *(long *)(param_1 + 0x68);
    }
    local_90 = *(long **)(param_1 + 0x70);
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
    local_98 = lVar9;
    (*pcVar8)(plVar7,&local_88,&local_98);
    plVar7 = local_90;
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
        piVar2 = (int *)((long)plVar7 + 0xc);
        do {
          iVar5 = *piVar2;
                    /* catch() { ... } // from try @ 02bc1a24 with catch @ 02bc1f4c */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
                    /* try { // try from 02bc1f60 to 02cc217f has its CatchHandler @ 02bc1f60
                       catch() { ... } // from try @ 02bc1f60 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc21b0 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc23d4 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc24cc with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc27a4 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc2a58 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc2b24 with catch @ 02bc1f60
                       catch() { ... } // from try @ 02bc2b94 with catch @ 02bc1f60 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_80;
    if (local_80 != (long *)0x0) {
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
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc2244
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest20ExecuteObjectMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1,undefined8 *param_2)

{
  int *piVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  char cVar5;
  bool bVar6;
  int iVar7;
  long lVar8;
  long *plVar9;
  undefined8 uVar10;
  long *plVar11;
  code *pcVar12;
  long *plVar13;
  long *local_d0;
  long *local_c8;
  undefined8 local_c0;
  long *local_b8;
  undefined8 local_b0;
  long *local_a8;
  undefined8 local_a0;
  long *local_98;
  undefined8 *local_90;
  long *local_88;
  undefined8 local_80;
  long *local_78;
  undefined8 *local_70;
  long *local_68;
  long *local_60;
  long *local_58;
  long *plStack_50;
  long local_48;
  
  lVar8 = tpidr_el0;
  local_48 = *(long *)(lVar8 + 0x28);
  if (*(long *)(param_1 + 0x38) == 0) {
    _ZN5Sfs2X8SmartFox14LastJoinedRoomEv(&local_60,*param_2);
    plVar9 = local_58;
    plVar11 = local_60;
    local_60 = (long *)0x0;
    local_58 = (long *)0x0;
    plVar13 = *(long **)(param_1 + 0x40);
    *(long **)(param_1 + 0x38) = plVar11;
    *(long **)(param_1 + 0x40) = plVar9;
    if (plVar13 != (long *)0x0) {
      plVar11 = plVar13 + 1;
      do {
        iVar7 = (int)*plVar11 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar11,0x10);
        if (bVar6) {
          *(int *)plVar11 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*plVar13 + 0x10))(plVar13);
        piVar1 = (int *)((long)plVar13 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar13 + 0x18))(plVar13);
        }
      }
    }
    plVar11 = local_58;
    if (local_58 != (long *)0x0) {
      plVar9 = local_58 + 1;
      do {
        iVar7 = (int)*plVar9 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar6) {
          *(int *)plVar9 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
                    /* try { // try from 02bc2888 to 02cc288f has its CatchHandler @ 02bc2ba4 */
        (**(code **)(*local_58 + 0x10))(local_58);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
                    /* try { // try from 02bc28b8 to 02cc28bf has its CatchHandler @ 02bc2ba0 */
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
  }
  plVar9 = (long *)_Znwm(0x18);
  plVar9[1] = 0;
  plVar9[2] = 0;
  *plVar9 = 0;
  local_58 = (long *)0x0;
  local_60 = plVar9;
  _ZN5boost6detail12shared_countC2ISt6vectorIlSaIlEEEEPT_(&plStack_50,plVar9);
  plVar11 = local_58;
  local_58 = plStack_50;
  plStack_50 = plVar11;
  if (plVar11 != (long *)0x0) {
    plVar13 = plVar11 + 1;
    do {
      iVar7 = (int)*plVar13 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar13,0x10);
      if (bVar6) {
        *(int *)plVar13 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_60,plVar9,plVar9);
  local_70 = (undefined8 *)_Znwm(8);
  *local_70 = 0;
  local_68 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_70,local_70,&local_68);
  uVar10 = (**(code **)**(undefined8 **)(param_1 + 0x38))();
  *local_70 = uVar10;
  plVar11 = *(long **)(param_1 + 8);
  pcVar12 = *(code **)(*plVar11 + 0x228);
  local_80 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_ROOM_IDE_03bd0e30;
  local_78 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_ROOM_IDE_03bd0e30 + 8);
  if (local_78 != (long *)0x0) {
    plVar9 = local_78 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  local_90 = local_70;
  local_88 = local_68;
  if (local_68 != (long *)0x0) {
    plVar9 = local_68 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  (*pcVar12)(plVar11,&local_80,&local_90);
  plVar11 = local_88;
  if (local_88 != (long *)0x0) {
    plVar9 = local_88 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02bc23cc to 02cc23d3 has its CatchHandler @ 02bc2bb0 */
                    /* try { // try from 02bc23d4 to 02cc24c3 has its CatchHandler @ 02bc1f60 */
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_78;
  if (local_78 != (long *)0x0) {
    plVar9 = local_78 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = *(long **)(param_1 + 8);
  pcVar12 = *(code **)(*plVar11 + 0x378);
  local_a0 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38
  ;
  local_98 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38 + 8
                       );
  if (local_98 != (long *)0x0) {
    plVar9 = local_98 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  local_b0 = *(undefined8 *)(param_1 + 0x68);
  local_a8 = *(long **)(param_1 + 0x70);
  if (local_a8 != (long *)0x0) {
    plVar9 = local_a8 + 1;
    do {
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = (int)*plVar9 + 1;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
  }
  (*pcVar12)(plVar11,&local_a0,&local_b0);
  plVar11 = local_a8;
                    /* try { // try from 02bc24c4 to 02cc24cb has its CatchHandler @ 02bc2bbc */
  if (local_a8 != (long *)0x0) {
                    /* try { // try from 02bc24cc to 02cc279b has its CatchHandler @ 02bc1f60 */
    plVar9 = local_a8 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_98;
  if (local_98 != (long *)0x0) {
    plVar9 = local_98 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (local_60[1] == *local_60) {
    plVar9 = *(long **)(param_1 + 0xb8);
    plVar11 = local_68;
    if (plVar9 != (long *)0x0) {
      lVar4 = plVar9[1];
      lVar3 = *plVar9;
      for (lVar2 = lVar3; lVar4 != lVar2; lVar2 = lVar2 + 0x10) {
        plVar11 = *(long **)(lVar2 + 8);
        if (plVar11 != (long *)0x0) {
          plVar13 = plVar11 + 1;
          do {
            iVar7 = (int)*plVar13 + -1;
            cVar5 = '\x01';
            bVar6 = (bool)ExclusiveMonitorPass(plVar13,0x10);
            if (bVar6) {
              *(int *)plVar13 = iVar7;
              cVar5 = ExclusiveMonitorsStatus();
            }
          } while (cVar5 != '\0');
          if (iVar7 == 0) {
            (**(code **)(*plVar11 + 0x10))(plVar11);
            piVar1 = (int *)((long)plVar11 + 0xc);
            do {
              iVar7 = *piVar1;
              cVar5 = '\x01';
              bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
              if (bVar6) {
                *piVar1 = iVar7 + -1;
                cVar5 = ExclusiveMonitorsStatus();
              }
            } while (cVar5 != '\0');
            if (iVar7 + -1 == 0) {
              (**(code **)(*plVar11 + 0x18))(plVar11);
            }
          }
        }
      }
      plVar9[1] = lVar3;
      plVar11 = local_68;
    }
  }
  else {
    plVar11 = *(long **)(param_1 + 8);
    pcVar12 = *(code **)(*plVar11 + 0x318);
    local_c0 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0
    ;
    local_b8 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 + 8
                         );
    if (local_b8 != (long *)0x0) {
      plVar9 = local_b8 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar6) {
          *(int *)plVar9 = (int)*plVar9 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    local_d0 = local_60;
    local_c8 = local_58;
    if (local_58 != (long *)0x0) {
      plVar9 = local_58 + 1;
      do {
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar6) {
          *(int *)plVar9 = (int)*plVar9 + 1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
    }
    (*pcVar12)(plVar11,&local_c0,&local_d0);
    plVar11 = local_c8;
    if (local_c8 != (long *)0x0) {
      plVar9 = local_c8 + 1;
      do {
        iVar7 = (int)*plVar9 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
        if (bVar6) {
          *(int *)plVar9 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_c8 + 0x10))(local_c8);
        piVar1 = (int *)((long)plVar11 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar11 + 0x18))(plVar11);
        }
      }
    }
    plVar9 = local_b8;
    plVar11 = local_68;
    if (local_b8 != (long *)0x0) {
      plVar13 = local_b8 + 1;
      do {
        iVar7 = (int)*plVar13 + -1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(plVar13,0x10);
        if (bVar6) {
          *(int *)plVar13 = iVar7;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_b8 + 0x10))(local_b8);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar7 = *piVar1;
          cVar5 = '\x01';
          bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar6) {
            *piVar1 = iVar7 + -1;
            cVar5 = ExclusiveMonitorsStatus();
          }
        } while (cVar5 != '\0');
        plVar11 = local_68;
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
          plVar11 = local_68;
        }
      }
    }
  }
  local_68 = plVar11;
  if (plVar11 != (long *)0x0) {
    plVar9 = plVar11 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*plVar11 + 0x10))(plVar11);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  plVar11 = local_58;
  if (local_58 != (long *)0x0) {
    plVar9 = local_58 + 1;
    do {
      iVar7 = (int)*plVar9 + -1;
      cVar5 = '\x01';
      bVar6 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar6) {
        *(int *)plVar9 = iVar7;
        cVar5 = ExclusiveMonitorsStatus();
      }
    } while (cVar5 != '\0');
    if (iVar7 == 0) {
                    /* try { // try from 02bc279c to 02cc27a3 has its CatchHandler @ 02bc2ba8 */
                    /* try { // try from 02bc27a4 to 02cc2887 has its CatchHandler @ 02bc1f60 */
      (**(code **)(*local_58 + 0x10))(local_58);
      piVar1 = (int *)((long)plVar11 + 0xc);
      do {
        iVar7 = *piVar1;
        cVar5 = '\x01';
        bVar6 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar6) {
          *piVar1 = iVar7 + -1;
          cVar5 = ExclusiveMonitorsStatus();
        }
      } while (cVar5 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar11 + 0x18))(plVar11);
      }
    }
  }
  if (*(long *)(lVar8 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc2cd4
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest19ExecuteBuddyMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  code *pcVar8;
  long lVar9;
  long local_98;
  long *local_90;
  undefined8 local_88;
  long *local_80;
  undefined8 local_78;
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  undefined8 local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
                    /* try { // try from 02bc2cf8 to 02cc2d07 has its CatchHandler @ 02bc2e10 */
  plVar7 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar7 + 0x228);
  local_48 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0;
  local_40 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 + 8);
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
                    /* try { // try from 02bc2d2c to 02cc2d2f has its CatchHandler @ 02bc2dfc */
  local_58 = *(undefined8 *)(param_1 + 0xa8);
                    /* try { // try from 02bc2d30 to 02cc2dbf has its CatchHandler @ 02bc2c60 */
  local_50 = *(long **)(param_1 + 0xb0);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar8)(plVar7,&local_48,&local_58);
  plVar7 = local_50;
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
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
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_40;
  if (local_40 != (long *)0x0) {
                    /* try { // try from 02bc2dc0 to 02cc2dc3 has its CatchHandler @ 02bc2df8 */
    plVar1 = local_40 + 1;
    do {
                    /* try { // try from 02bc2dc4 to 02cc2e2b has its CatchHandler @ 02bc2c60 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)plVar7 + 0xc);
      do {
        iVar5 = *piVar2;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02bc2dc0 with catch @ 02bc2df8 */
      } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02bc2d2c with catch @ 02bc2dfc */
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
                    /* catch() { ... } // from try @ 02bc2cf8 with catch @ 02bc2e10 */
  plVar7 = *(long **)(param_1 + 8);
  pcVar8 = *(code **)(*plVar7 + 0x2a8);
  local_68 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88;
  local_60 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88 + 8);
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
  local_78 = *(undefined8 *)(param_1 + 0x58);
  local_70 = *(long **)(param_1 + 0x60);
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
  (*pcVar8)(plVar7,&local_68,&local_78);
  plVar7 = local_70;
  if (local_70 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_60;
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
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
      (**(code **)(*local_60 + 0x10))(local_60);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* catch() { ... } // from try @ 02bc2f98 with catch @ 02bc2f1c
                       catch() { ... } // from try @ 02bc30b4 with catch @ 02bc2f1c */
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  lVar9 = *(long *)(param_1 + 0x68);
  if (lVar9 != 0) {
    plVar7 = *(long **)(param_1 + 8);
    pcVar8 = *(code **)(*plVar7 + 0x378);
    local_88 = *(undefined8 *)
                PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38;
    local_80 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38 +
                         8);
    if (local_80 != (long *)0x0) {
      plVar1 = local_80 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      lVar9 = *(long *)(param_1 + 0x68);
    }
    local_90 = *(long **)(param_1 + 0x70);
    if (local_90 != (long *)0x0) {
      plVar1 = local_90 + 1;
      do {
                    /* try { // try from 02bc2f84 to 02cc2f8b has its CatchHandler @ 02bc3090 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
                    /* try { // try from 02bc2f90 to 02cc2f97 has its CatchHandler @ 02bc3020 */
    local_98 = lVar9;
    (*pcVar8)(plVar7,&local_88,&local_98);
    plVar7 = local_90;
                    /* try { // try from 02bc2f98 to 02cc309f has its CatchHandler @ 02bc2f1c */
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
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_80;
    if (local_80 != (long *)0x0) {
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
                    /* catch() { ... } // from try @ 02bc2f90 with catch @ 02bc3020 */
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE
// ADDRESS : 02bc32cc
================================================================

void _ZN5Sfs2X8Requests21GenericMessageRequest23ExecuteSuperUserMessageEN5boost10shared_ptrINS_8SmartFoxEEE
               (long param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  undefined8 uVar8;
  code *pcVar9;
  long lVar10;
  undefined8 local_128;
  long *local_120;
  undefined8 local_118;
  long *local_110;
  undefined8 *local_108;
  long *local_100;
  undefined8 local_f8;
  long *local_f0;
  undefined8 *local_e8;
  long *local_e0;
  undefined8 *local_d8;
  long *local_d0;
  undefined8 local_c8;
  long *local_c0;
  undefined8 *local_b8;
  long *local_b0;
  undefined8 *local_a8;
  long *local_a0;
  undefined8 local_98;
  long *local_90;
  undefined8 *local_88;
  long *local_80;
  long local_78;
  long *local_70;
  undefined8 local_68;
  long *local_60;
  undefined8 local_58;
  long *local_50;
  undefined8 local_48;
  long *local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x2a8);
  local_48 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88;
  local_40 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest11KEY_MESSAGEE_03bd0d88 + 8);
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  local_58 = *(undefined8 *)(param_1 + 0x58);
  local_50 = *(long **)(param_1 + 0x60);
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar9)(plVar7,&local_48,&local_58);
  plVar7 = local_50;
  if (local_50 != (long *)0x0) {
    plVar1 = local_50 + 1;
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
      (**(code **)(*local_50 + 0x10))(local_50);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_40;
  if (local_40 != (long *)0x0) {
    plVar1 = local_40 + 1;
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
      (**(code **)(*local_40 + 0x10))(local_40);
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  lVar10 = *(long *)(param_1 + 0x68);
  if (lVar10 != 0) {
    plVar7 = *(long **)(param_1 + 8);
    pcVar9 = *(code **)(*plVar7 + 0x378);
    local_68 = *(undefined8 *)
                PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38;
    local_60 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest15KEY_XTRA_PARAMSE_03bdac38 +
                         8);
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
      lVar10 = *(long *)(param_1 + 0x68);
    }
    local_70 = *(long **)(param_1 + 0x70);
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
    local_78 = lVar10;
    (*pcVar9)(plVar7,&local_68,&local_78);
    plVar7 = local_70;
    if (local_70 != (long *)0x0) {
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
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_60;
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
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
        (**(code **)(*local_60 + 0x10))(local_60);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  local_88 = (undefined8 *)_Znwm(8);
  *local_88 = 0;
  local_80 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_88,local_88,&local_80);
  *local_88 = *(undefined8 *)(param_1 + 200);
  plVar7 = *(long **)(param_1 + 8);
  pcVar9 = *(code **)(*plVar7 + 0x228);
  local_98 = *(undefined8 *)
              PTR__ZN5Sfs2X8Requests21GenericMessageRequest18KEY_RECIPIENT_MODEE_03bd4478;
  local_90 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest18KEY_RECIPIENT_MODEE_03bd4478
                       + 8);
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
  local_a8 = local_88;
  local_a0 = local_80;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
  }
  (*pcVar9)(plVar7,&local_98,&local_a8);
  plVar7 = local_a0;
  if (local_a0 != (long *)0x0) {
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  plVar7 = local_90;
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
      piVar2 = (int *)((long)plVar7 + 0xc);
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
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  iVar5 = *(int *)(param_1 + 200);
  if (iVar5 == 0) {
    local_b8 = (undefined8 *)_Znwm(8);
    *local_b8 = 0;
    local_b0 = (long *)0x0;
    _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_b8,local_b8,&local_b0);
                    /* try { // try from 02bc3984 to 02cc3987 has its CatchHandler @ 02bc39a8 */
    uVar8 = (**(code **)**(undefined8 **)(param_1 + 0x78))();
    *local_b8 = uVar8;
    plVar7 = *(long **)(param_1 + 8);
    pcVar9 = *(code **)(*plVar7 + 0x228);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc3984 with catch @ 02bc39a8
                        */
    local_c8 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0
    ;
    local_c0 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 + 8
                         );
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
    local_d8 = local_b8;
    local_d0 = local_b0;
    if (local_b0 != (long *)0x0) {
      plVar1 = local_b0 + 1;
      do {
                    /* try { // try from 02bc39e0 to 02cc39e3 has its CatchHandler @ 02bc39fc */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    (*pcVar9)(plVar7,&local_c8,&local_d8);
    plVar7 = local_d0;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc39e0 with catch @ 02bc39fc
                        */
    if (local_d0 != (long *)0x0) {
      plVar1 = local_d0 + 1;
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
        (**(code **)(*local_d0 + 0x10))(local_d0);
        piVar2 = (int *)((long)plVar7 + 0xc);
        do {
          iVar5 = *piVar2;
                    /* try { // try from 02bc3a34 to 02cc3a37 has its CatchHandler @ 02bc3a58 */
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_c0;
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc3a34 with catch @ 02bc3a58
                        */
    if (local_c0 != (long *)0x0) {
      plVar1 = local_c0 + 1;
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
        (**(code **)(*local_c0 + 0x10))(local_c0);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* try { // try from 02bc3a9c to 02cc3a9f has its CatchHandler @ 02bc3ab8 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_b0;
    if (local_b0 != (long *)0x0) {
      plVar1 = local_b0 + 1;
      do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc3a9c with catch @ 02bc3ab8
                        */
        iVar5 = (int)*plVar1 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
        (**(code **)(*local_b0 + 0x10))(local_b0);
        piVar2 = (int *)((long)plVar7 + 0xc);
        do {
          iVar5 = *piVar2;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
          if (bVar4) {
            *piVar2 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
                    /* try { // try from 02bc3af0 to 02cc3af3 has its CatchHandler @ 02bc3b14 */
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  else if (iVar5 == 1) {
    local_e8 = (undefined8 *)_Znwm(8);
    *local_e8 = 0;
    local_e0 = (long *)0x0;
    _ZN5boost6detail20sp_pointer_constructIllEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
              (&local_e8,local_e8,&local_e0);
    uVar8 = (**(code **)**(undefined8 **)(param_1 + 0x88))();
                    /* try { // try from 02bc37dc to 02cc37df has its CatchHandler @ 02bc37f8 */
    *local_e8 = uVar8;
    plVar7 = *(long **)(param_1 + 8);
    pcVar9 = *(code **)(*plVar7 + 0x228);
    local_f8 = *(undefined8 *)PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0
    ;
    local_f0 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 + 8
                         );
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc37dc with catch @ 02bc37f8
                        */
                    /* try { // try from 02bc37fc to 02cc3873 has its CatchHandler @ 02bc37fc
                       catch() { ... } // from try @ 02bc37fc with catch @ 02bc37fc
                       catch() { ... } // from try @ 02bc38b8 with catch @ 02bc37fc */
    if (local_f0 != (long *)0x0) {
      plVar1 = local_f0 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    local_108 = local_e8;
    local_100 = local_e0;
    if (local_e0 != (long *)0x0) {
      plVar1 = local_e0 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    (*pcVar9)(plVar7,&local_f8,&local_108);
    plVar7 = local_100;
    if (local_100 != (long *)0x0) {
      plVar1 = local_100 + 1;
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
                    /* try { // try from 02bc3874 to 02cc3877 has its CatchHandler @ 02bc38cc */
        (**(code **)(*local_100 + 0x10))(local_100);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_f0;
    if (local_f0 != (long *)0x0) {
      plVar1 = local_f0 + 1;
      do {
                    /* try { // try from 02bc38b0 to 02cc38b7 has its CatchHandler @ 02bc38e8 */
        iVar5 = (int)*plVar1 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* try { // try from 02bc38b8 to 02cc3903 has its CatchHandler @ 02bc37fc */
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
                    /* catch() { ... } // from try @ 02bc3874 with catch @ 02bc38cc */
        (**(code **)(*local_f0 + 0x10))(local_f0);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* catch() { ... } // from try @ 02bc38b0 with catch @ 02bc38e8 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_e0;
    if (local_e0 != (long *)0x0) {
      plVar1 = local_e0 + 1;
      do {
                    /* try { // try from 02bc3904 to 02cc391f has its CatchHandler @ 02bc3904
                       catch() { ... } // from try @ 02bc3904 with catch @ 02bc3904
                       catch() { ... } // from try @ 02bc3928 with catch @ 02bc3904 */
        iVar5 = (int)*plVar1 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
                    /* try { // try from 02bc3920 to 02cc3927 has its CatchHandler @ 02bc3940 */
        (**(code **)(*local_e0 + 0x10))(local_e0);
                    /* try { // try from 02bc3928 to 02cc3953 has its CatchHandler @ 02bc3904 */
        piVar2 = (int *)((long)plVar7 + 0xc);
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
                    /* catch() { ... } // from try @ 02bc3920 with catch @ 02bc3940 */
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  else if (iVar5 == 2) {
    plVar7 = *(long **)(param_1 + 8);
    pcVar9 = *(code **)(*plVar7 + 0x2a8);
    local_118 = *(undefined8 *)
                 PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0;
    local_110 = *(long **)(PTR__ZN5Sfs2X8Requests21GenericMessageRequest13KEY_RECIPIENTE_03bdaad0 +
                          8);
    if (local_110 != (long *)0x0) {
      plVar1 = local_110 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    local_128 = *(undefined8 *)(param_1 + 0x98);
    local_120 = *(long **)(param_1 + 0xa0);
    if (local_120 != (long *)0x0) {
      plVar1 = local_120 + 1;
      do {
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar4) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
    }
    (*pcVar9)(plVar7,&local_118,&local_128);
    plVar7 = local_120;
    if (local_120 != (long *)0x0) {
      plVar1 = local_120 + 1;
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
        (**(code **)(*local_120 + 0x10))(local_120);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
    plVar7 = local_110;
    if (local_110 != (long *)0x0) {
      plVar1 = local_110 + 1;
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
        (**(code **)(*local_110 + 0x10))(local_110);
        piVar2 = (int *)((long)plVar7 + 0xc);
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
          (**(code **)(*plVar7 + 0x18))(plVar7);
        }
      }
    }
  }
  plVar7 = local_80;
  if (local_80 != (long *)0x0) {
    plVar1 = local_80 + 1;
    do {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bc3af0 with catch @ 02bc3b14
                        */
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
      piVar2 = (int *)((long)plVar7 + 0xc);
      do {
        iVar5 = *piVar2;
                    /* catch() { ... } // from try @ 02bc3ba4 with catch @ 02bc3b3c */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar2,0x10);
        if (bVar4) {
          *piVar2 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar7 + 0x18))(plVar7);
      }
    }
  }
  if (*(long *)(lVar6 + 0x28) == local_38) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs
// ADDRESS : 02bc42bc
================================================================

void _ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs
               (long *param_1,undefined8 param_2,long *param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined8 uVar5;
  int *piVar6;
  int iVar7;
  long *plVar8;
  code *pcVar9;
  undefined1 auStack_f0 [8];
  long *local_e8;
  undefined8 local_e0;
  long *local_d8;
  undefined1 *local_d0;
  long *local_c8;
  undefined1 auStack_c0 [8];
  long local_b8;
  undefined1 *local_b0;
  long *local_a8;
  undefined1 auStack_a0 [8];
  long *local_98;
  undefined8 local_90;
  long *local_88;
  undefined1 auStack_80 [8];
  long *local_78;
  undefined8 local_70;
  long *local_68;
  long local_58;
  
  lVar4 = tpidr_el0;
  local_58 = *(long *)(lVar4 + 0x28);
                    /* catch() { ... } // from try @ 02bc4098 with catch @ 02bc42f4 */
  _ZN5Sfs2X8Requests11BaseRequestC1ENS0_11RequestTypeE(param_1,0);
  plVar8 = (long *)param_1[1];
                    /* try { // try from 02bc4304 to 02cc431b has its CatchHandler @ 02bc431c */
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests16HandshakeRequestE_03bd2400 + 0x10);
                    /* catch() { ... } // from try @ 02bc4304 with catch @ 02bc431c */
  pcVar9 = *(code **)(*plVar8 + 0x2a8);
                    /* try { // try from 02bc4320 to 02cc4323 has its CatchHandler @ 02bc4328 */
  local_70 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16HandshakeRequest7KEY_APIE_03bd8a38;
  local_68 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest7KEY_APIE_03bd8a38 + 8);
                    /* try { // try from 02bc4324 to 02cc446f has its CatchHandler @ 02bc3bf8 */
                    /* catch() { ... } // from try @ 02bc4320 with catch @ 02bc4328 */
  if (local_68 != (long *)0x0) {
                    /* catch() { ... } // from try @ 02bc3cf8 with catch @ 02bc432c */
    plVar1 = local_68 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  uVar5 = _Znwm(8);
  FUN_0307e06c(uVar5,param_2);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_80,uVar5);
  (*pcVar9)(plVar8,&local_70,auStack_80);
  if (local_78 != (long *)0x0) {
    plVar8 = local_78 + 1;
    do {
      iVar7 = (int)*plVar8 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
                    /* catch() { ... } // from try @ 02bc3f0c with catch @ 02bc4394 */
                    /* catch() { ... } // from try @ 02bc3e70 with catch @ 02bc4398 */
      (**(code **)(*local_78 + 0x10))(local_78);
      piVar6 = (int *)((long)local_78 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_78 + 0x18))(local_78);
      }
    }
  }
  plVar8 = local_68;
  if (local_68 != (long *)0x0) {
    plVar1 = local_68 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_68 + 0x10))(local_68);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  plVar8 = (long *)param_1[1];
  pcVar9 = *(code **)(*plVar8 + 0x2a8);
  local_90 = *(undefined8 *)PTR__ZN5Sfs2X8Requests16HandshakeRequest15KEY_CLIENT_TYPEE_03bda620;
  local_88 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest15KEY_CLIENT_TYPEE_03bda620 + 8);
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  uVar5 = _Znwm(8);
  FUN_0307e06c(uVar5,param_4);
  _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_a0,uVar5);
  (*pcVar9)(plVar8,&local_90,auStack_a0);
  if (local_98 != (long *)0x0) {
    plVar8 = local_98 + 1;
    do {
      iVar7 = (int)*plVar8 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
      if (bVar3) {
        *(int *)plVar8 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_98 + 0x10))(local_98);
      piVar6 = (int *)((long)local_98 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*local_98 + 0x18))(local_98);
      }
    }
  }
  plVar8 = local_88;
  if (local_88 != (long *)0x0) {
    plVar1 = local_88 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_88 + 0x10))(local_88);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  local_b0 = (undefined1 *)_Znwm(1);
  *local_b0 = 0;
  local_a8 = (long *)0x0;
  _ZN5boost6detail20sp_pointer_constructIbbEEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (&local_b0,local_b0,&local_a8);
  *local_b0 = 1;
  plVar8 = (long *)param_1[1];
  pcVar9 = *(code **)(*plVar8 + 0x1c0);
  FUN_0307a6fc(&local_b8,&DAT_03245e63,auStack_c0);
  local_d0 = local_b0;
  local_c8 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar1 = local_a8 + 1;
    do {
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = (int)*plVar1 + 1;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
  }
  (*pcVar9)(plVar8,&local_b8,&local_d0);
  plVar8 = local_c8;
  if (local_c8 != (long *)0x0) {
    plVar1 = local_c8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_c8 + 0x10))(local_c8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
  if ((undefined *)(local_b8 + -0x18) != PTR_DAT_03c37adf_1_03bd0478) {
    piVar6 = (int *)(local_b8 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar7 = *piVar6;
      *piVar6 = iVar7 + -1;
    }
    else {
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar7 < 1) {
      _ZdlPv((undefined *)(local_b8 + -0x18));
    }
  }
  if (*(long *)(*param_3 + -0x18) != 0) {
    plVar8 = (long *)param_1[1];
    pcVar9 = *(code **)(*plVar8 + 0x2a8);
    local_e0 = *(undefined8 *)
                PTR__ZN5Sfs2X8Requests16HandshakeRequest22KEY_RECONNECTION_TOKENE_03bd7580;
    local_d8 = *(long **)(PTR__ZN5Sfs2X8Requests16HandshakeRequest22KEY_RECONNECTION_TOKENE_03bd7580
                         + 8);
    if (local_d8 != (long *)0x0) {
      plVar1 = local_d8 + 1;
      do {
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = (int)*plVar1 + 1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    uVar5 = _Znwm(8);
    FUN_0307e06c(uVar5,param_3);
                    /* try { // try from 02bc4698 to 02cc47ab has its CatchHandler @ 02bc4698
                       catch() { ... } // from try @ 02bc4698 with catch @ 02bc4698
                       catch() { ... } // from try @ 02bc47b4 with catch @ 02bc4698 */
    _ZN5boost10shared_ptrISsEC2ISsEEPT_(auStack_f0,uVar5);
    (*pcVar9)(plVar8,&local_e0,auStack_f0);
    if (local_e8 != (long *)0x0) {
      plVar8 = local_e8 + 1;
      do {
        iVar7 = (int)*plVar8 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar8,0x10);
        if (bVar3) {
          *(int *)plVar8 = iVar7;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_e8 + 0x10))(local_e8);
        piVar6 = (int *)((long)local_e8 + 0xc);
        do {
          iVar7 = *piVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar3) {
            *piVar6 = iVar7 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*local_e8 + 0x18))(local_e8);
        }
      }
    }
    plVar8 = local_d8;
    if (local_d8 != (long *)0x0) {
      plVar1 = local_d8 + 1;
      do {
        iVar7 = (int)*plVar1 + -1;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
        if (bVar3) {
          *(int *)plVar1 = iVar7;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 == 0) {
        (**(code **)(*local_d8 + 0x10))(local_d8);
        piVar6 = (int *)((long)plVar8 + 0xc);
        do {
          iVar7 = *piVar6;
          cVar2 = '\x01';
          bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
          if (bVar3) {
            *piVar6 = iVar7 + -1;
            cVar2 = ExclusiveMonitorsStatus();
          }
        } while (cVar2 != '\0');
        if (iVar7 + -1 == 0) {
          (**(code **)(*plVar8 + 0x18))(plVar8);
        }
      }
    }
  }
  plVar8 = local_a8;
  if (local_a8 != (long *)0x0) {
    plVar1 = local_a8 + 1;
    do {
      iVar7 = (int)*plVar1 + -1;
      cVar2 = '\x01';
      bVar3 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar3) {
        *(int *)plVar1 = iVar7;
        cVar2 = ExclusiveMonitorsStatus();
      }
    } while (cVar2 != '\0');
    if (iVar7 == 0) {
      (**(code **)(*local_a8 + 0x10))(local_a8);
      piVar6 = (int *)((long)plVar8 + 0xc);
      do {
        iVar7 = *piVar6;
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar6,0x10);
        if (bVar3) {
          *piVar6 = iVar7 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
      if (iVar7 + -1 == 0) {
                    /* try { // try from 02bc47ac to 02cc47b3 has its CatchHandler @ 02bc47b4 */
        (**(code **)(*plVar8 + 0x18))(plVar8);
      }
    }
  }
                    /* catch() { ... } // from try @ 02bc47ac with catch @ 02bc47b4
                       try { // try from 02bc47b4 to 02cc47c7 has its CatchHandler @ 02bc4698 */
  if (*(long *)(lVar4 + 0x28) != local_58) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16HandshakeRequestD1Ev  [thunk -> 0x2ba58c8]
// ADDRESS : 02bc4c98
================================================================

void _ZN5Sfs2X8Requests11BaseRequestD1Ev(long *param_1)

{
  long *plVar1;
  int *piVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long *plVar6;
  
  plVar6 = (long *)param_1[2];
  *param_1 = (long)(PTR__ZTVN5Sfs2X8Requests11BaseRequestE_03bdac70 + 0x10);
  if (plVar6 != (long *)0x0) {
    plVar1 = plVar6 + 1;
    do {
                    /* try { // try from 02ba58f4 to 02ca58fb has its CatchHandler @ 02ba5900 */
      iVar5 = (int)*plVar1 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar1,0x10);
      if (bVar4) {
        *(int *)plVar1 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02ba58fc to 02ca59cf has its CatchHandler @ 02ba576c */
    } while (cVar3 != '\0');
                    /* catch() { ... } // from try @ 02ba58f4 with catch @ 02ba5900 */
    if (iVar5 == 0) {
      (**(code **)(*plVar6 + 0x10))(plVar6);
      piVar2 = (int *)((long)plVar6 + 0xc);
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
        (**(code **)(*plVar6 + 0x18))(plVar6);
      }
    }
  }
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Requests16HandshakeRequestD0Ev
// ADDRESS : 02bc4c9c
================================================================

void _ZN5Sfs2X8Requests16HandshakeRequestD0Ev(void *param_1)

{
  _ZN5Sfs2X8Requests11BaseRequestD1Ev();
  _ZdlPv(param_1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X8Bitswarm13PendingPacketC1EN5boost10shared_ptrINS_4Core12PacketHeaderEEE
// ADDRESS : 02bdda90
================================================================

void _ZN5Sfs2X8Bitswarm13PendingPacketC1EN5boost10shared_ptrINS_4Core12PacketHeaderEEE
               (undefined8 *param_1,undefined8 *param_2)

{
  int *piVar1;
  long lVar2;
  char cVar3;
  bool bVar4;
  int iVar5;
  long lVar6;
  uint uVar7;
  undefined8 uVar8;
  long *plVar9;
  long *plVar10;
  undefined8 local_50;
  long *local_48;
  undefined8 local_40;
  long local_38;
  
  lVar6 = tpidr_el0;
  local_38 = *(long *)(lVar6 + 0x28);
  param_1[1] = 0;
  *param_1 = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  uVar8 = *param_2;
  lVar2 = param_2[1];
  if (lVar2 == 0) {
    *param_1 = uVar8;
    param_1[1] = 0;
  }
  else {
    piVar1 = (int *)(lVar2 + 8);
    do {
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
      if (bVar4) {
        *piVar1 = *piVar1 + 1;
        cVar3 = ExclusiveMonitorsStatus();
      }
                    /* try { // try from 02bddad8 to 02cddadf has its CatchHandler @ 02bddb44 */
    } while (cVar3 != '\0');
    plVar9 = (long *)param_1[1];
    *param_1 = uVar8;
    param_1[1] = lVar2;
    if (plVar9 != (long *)0x0) {
      plVar10 = plVar9 + 1;
      do {
        iVar5 = (int)*plVar10 + -1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
        if (bVar4) {
          *(int *)plVar10 = iVar5;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 == 0) {
                    /* try { // try from 02bddb08 to 02cddb37 has its CatchHandler @ 02bddb48 */
        (**(code **)(*plVar9 + 0x10))(plVar9);
        piVar1 = (int *)((long)plVar9 + 0xc);
        do {
          iVar5 = *piVar1;
          cVar3 = '\x01';
          bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
          if (bVar4) {
            *piVar1 = iVar5 + -1;
            cVar3 = ExclusiveMonitorsStatus();
          }
        } while (cVar3 != '\0');
        if (iVar5 + -1 == 0) {
          (**(code **)(*plVar9 + 0x18))(plVar9);
        }
      }
    }
  }
                    /* catch() { ... } // from try @ 02bddad8 with catch @ 02bddb44 */
  uVar8 = _Znwm(0x890);
                    /* catch() { ... } // from try @ 02bddb08 with catch @ 02bddb48 */
                    /* catch() { ... } // from try @ 02bddbe4 with catch @ 02bddb4c
                       catch() { ... } // from try @ 02bddc28 with catch @ 02bddb4c */
  _ZN5Sfs2X4Util9ByteArrayC2Ev(uVar8);
  local_48 = (long *)0x0;
  local_50 = uVar8;
  _ZN5boost6detail12shared_countC2IN5Sfs2X4Util9ByteArrayEEEPT_(&local_40,uVar8);
                    /* try { // try from 02bddb68 to 02cddb6f has its CatchHandler @ 02bddc04 */
  local_48 = (long *)local_40;
  _ZN5boost6detail26sp_enable_shared_from_thisEz(&local_50,uVar8,uVar8);
  plVar9 = local_48;
  uVar8 = local_50;
  local_50 = 0;
  local_48 = (long *)0x0;
  plVar10 = (long *)param_1[3];
  param_1[2] = uVar8;
  param_1[3] = plVar9;
  if (plVar10 != (long *)0x0) {
    plVar9 = plVar10 + 1;
    do {
      iVar5 = (int)*plVar9 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar9,0x10);
      if (bVar4) {
        *(int *)plVar9 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* try { // try from 02bddbb4 to 02cddbe3 has its CatchHandler @ 02bddc00 */
      (**(code **)(*plVar10 + 0x10))(plVar10);
      piVar1 = (int *)((long)plVar10 + 0xc);
      do {
        iVar5 = *piVar1;
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
      } while (cVar3 != '\0');
      if (iVar5 + -1 == 0) {
        (**(code **)(*plVar10 + 0x18))(plVar10);
      }
    }
  }
  plVar9 = local_48;
                    /* try { // try from 02bddbe4 to 02cddc1b has its CatchHandler @ 02bddb4c */
  if (local_48 != (long *)0x0) {
    plVar10 = local_48 + 1;
    do {
      iVar5 = (int)*plVar10 + -1;
      cVar3 = '\x01';
      bVar4 = (bool)ExclusiveMonitorPass(plVar10,0x10);
      if (bVar4) {
        *(int *)plVar10 = iVar5;
        cVar3 = ExclusiveMonitorsStatus();
      }
    } while (cVar3 != '\0');
    if (iVar5 == 0) {
                    /* catch() { ... } // from try @ 02bddbb4 with catch @ 02bddc00 */
                    /* catch() { ... } // from try @ 02bddb68 with catch @ 02bddc04 */
      (**(code **)(*local_48 + 0x10))(local_48);
      piVar1 = (int *)((long)plVar9 + 0xc);
      do {
        iVar5 = *piVar1;
                    /* try { // try from 02bddc1c to 02cddc1f has its CatchHandler @ 02bddc20 */
        cVar3 = '\x01';
        bVar4 = (bool)ExclusiveMonitorPass(piVar1,0x10);
        if (bVar4) {
          *piVar1 = iVar5 + -1;
          cVar3 = ExclusiveMonitorsStatus();
        }
                    /* catch() { ... } // from try @ 02bddc1c with catch @ 02bddc20 */
      } while (cVar3 != '\0');
                    /* try { // try from 02bddc24 to 02cddc27 has its CatchHandler @ 02bddc30 */
      if (iVar5 + -1 == 0) {
                    /* try { // try from 02bddc28 to 02cddc33 has its CatchHandler @ 02bddb4c */
                    /* catch() { ... } // from try @ 02bddc24 with catch @ 02bddc30 */
        (**(code **)(*plVar9 + 0x18))(plVar9);
      }
    }
  }
  uVar8 = param_1[2];
  uVar7 = _ZN5Sfs2X4Core12PacketHeader10CompressedEv(*param_2);
  _ZN5Sfs2X4Util9ByteArray10CompressedEb(uVar8,uVar7 & 1);
  if (*(long *)(lVar6 + 0x28) == local_38) {
                    /* catch(type#1 @ 00000000) { ... } // from try @ 02bddc88 with catch @ 02bddc68
                       catch(type#1 @ 00000000) { ... } // from try @ 02bddcd4 with catch @ 02bddc68
                        */
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeaderC2Ebbbb
// ADDRESS : 02bddf28
================================================================

void _ZN5Sfs2X4Core12PacketHeaderC2Ebbbb
               (undefined8 *param_1,byte param_2,byte param_3,byte param_4,byte param_5)

{
                    /* catch() { ... } // from try @ 02bde050 with catch @ 02bddf28
                       catch() { ... } // from try @ 02bde130 with catch @ 02bddf28 */
  *(undefined1 *)(param_1 + 1) = 1;
  *param_1 = 0xffffffffffffffff;
  *(byte *)((long)param_1 + 9) = param_3 & 1;
  *(byte *)((long)param_1 + 10) = param_2 & 1;
  *(byte *)((long)param_1 + 0xb) = param_4 & 1;
  *(byte *)((long)param_1 + 0xc) = param_5 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv
// ADDRESS : 02bddf5c
================================================================

undefined8 _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEv(undefined8 *param_1)

{
  return *param_1;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl
// ADDRESS : 02bddf64
================================================================

void _ZN5Sfs2X4Core12PacketHeader14ExpectedLengthEl(undefined8 *param_1,undefined8 param_2)

{
  *param_1 = param_2;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader9EncryptedEv
// ADDRESS : 02bddf6c
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader9EncryptedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 10);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader9EncryptedEb
// ADDRESS : 02bddf74
================================================================

void _ZN5Sfs2X4Core12PacketHeader9EncryptedEb(long param_1,byte param_2)

{
  *(byte *)(param_1 + 10) = param_2 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader10CompressedEv
// ADDRESS : 02bddf80
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader10CompressedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 9);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader10CompressedEb
// ADDRESS : 02bddf88
================================================================

void _ZN5Sfs2X4Core12PacketHeader10CompressedEb(long param_1,byte param_2)

{
  *(byte *)(param_1 + 9) = param_2 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader9BlueBoxedEv
// ADDRESS : 02bddf94
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader9BlueBoxedEv(long param_1)

{
                    /* try { // try from 02bddf94 to 02cddf9f has its CatchHandler @ 02bde07c */
  return *(undefined1 *)(param_1 + 0xb);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader9BlueBoxedEb
// ADDRESS : 02bddf9c
================================================================

void _ZN5Sfs2X4Core12PacketHeader9BlueBoxedEb(long param_1,byte param_2)

{
  *(byte *)(param_1 + 0xb) = param_2 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader6BinaryEv
// ADDRESS : 02bddfa8
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader6BinaryEv(long param_1)

{
  return *(undefined1 *)(param_1 + 8);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader6BinaryEb
// ADDRESS : 02bddfb0
================================================================

void _ZN5Sfs2X4Core12PacketHeader6BinaryEb(long param_1,byte param_2)

{
  *(byte *)(param_1 + 8) = param_2 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader8BigSizedEv
// ADDRESS : 02bddfbc
================================================================

undefined1 _ZN5Sfs2X4Core12PacketHeader8BigSizedEv(long param_1)

{
  return *(undefined1 *)(param_1 + 0xc);
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader8BigSizedEb
// ADDRESS : 02bddfc4
================================================================

void _ZN5Sfs2X4Core12PacketHeader8BigSizedEb(long param_1,byte param_2)

{
                    /* try { // try from 02bddfc8 to 02cddff7 has its CatchHandler @ 02bde078 */
  *(byte *)(param_1 + 0xc) = param_2 & 1;
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader10FromBinaryEl
// ADDRESS : 02bddfd0
================================================================

void _ZN5Sfs2X4Core12PacketHeader10FromBinaryEl(undefined8 *param_1,uint param_2)

{
  undefined8 *puVar1;
  
  puVar1 = (undefined8 *)_Znwm(0x10);
  *(undefined1 *)(puVar1 + 1) = 1;
  *param_1 = puVar1;
  *puVar1 = 0xffffffffffffffff;
  *(byte *)((long)puVar1 + 9) = (byte)(param_2 >> 5) & 1;
  *(byte *)((long)puVar1 + 10) = (byte)(param_2 >> 6) & 1;
                    /* try { // try from 02bde020 to 02cde04f has its CatchHandler @ 02bde074 */
  *(byte *)((long)puVar1 + 0xb) = (byte)(param_2 >> 4) & 1;
  *(byte *)((long)puVar1 + 0xc) = (byte)(param_2 >> 3) & 1;
  param_1[1] = 0;
  _ZN5boost6detail20sp_pointer_constructIN5Sfs2X4Core12PacketHeaderES4_EEvPNS_10shared_ptrIT_EEPT0_RNS0_12shared_countE
            (param_1,puVar1,param_1 + 1);
  return;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader6EncodeEv
// ADDRESS : 02bde0b0
================================================================

uint _ZN5Sfs2X4Core12PacketHeader6EncodeEv(long param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  if (*(char *)(param_1 + 8) != '\0') {
    uVar1 = 0xffffff80;
  }
  if (*(char *)(param_1 + 10) != '\0') {
    uVar1 = uVar1 | 0x40;
  }
  if (*(char *)(param_1 + 9) != '\0') {
    uVar1 = uVar1 | 0x20;
  }
  if (*(char *)(param_1 + 0xb) != '\0') {
    uVar1 = uVar1 | 0x10;
  }
  if (*(char *)(param_1 + 0xc) != '\0') {
    uVar1 = uVar1 | 8;
  }
                    /* try { // try from 02bde100 to 02cde12f has its CatchHandler @ 02bde13c */
  return uVar1;
}



================================================================
// FUNCTION: _ZN5Sfs2X4Core12PacketHeader8ToStringEv
// ADDRESS : 02bde104
================================================================

void _ZN5Sfs2X4Core12PacketHeader8ToStringEv(undefined8 *param_1,long param_2)

{
  undefined *puVar1;
  char cVar2;
  bool bVar3;
  long lVar4;
  undefined *puVar5;
  long *plVar6;
  size_t sVar7;
  int *piVar8;
  int iVar9;
  undefined *local_b8;
  undefined8 local_b0 [13];
  long local_48;
  
  lVar4 = tpidr_el0;
  local_48 = *(long *)(lVar4 + 0x28);
                    /* try { // try from 02bde130 to 02cde13f has its CatchHandler @ 02bddf28 */
  plVar6 = (long *)_Znwm(8);
  puVar5 = PTR_DAT_03c37adf_1_03bd0478;
                    /* catch() { ... } // from try @ 02bde0a8 with catch @ 02bde138 */
                    /* catch() { ... } // from try @ 02bde100 with catch @ 02bde13c */
                    /* catch() { ... } // from try @ 02bde664 with catch @ 02bde140
                       catch() { ... } // from try @ 02bde9f8 with catch @ 02bde140 */
  puVar1 = PTR_DAT_03c37adf_1_03bd0478 + 0x18;
  *plVar6 = (long)puVar1;
  *param_1 = plVar6;
  param_1[1] = 0;
  _ZN5boost6detail12shared_countC2ISsEEPT_(local_b0,plVar6);
  param_1[1] = local_b0[0];
  _ZN5boost6detail26sp_enable_shared_from_thisEz(param_1,plVar6,plVar6);
  local_b8 = puVar1;
  FUN_0307b318(*param_1,"---------------------------------------------\n",0x2e);
                    /* try { // try from 02bde19c to 02cde1bf has its CatchHandler @ 02bde8c0 */
  FUN_0307c7fc(&local_b8,0,*(undefined8 *)(local_b8 + -0x18),0);
  sprintf((char *)local_b0,"Binary:  \t %d \n",(ulong)*(byte *)(param_2 + 8));
  sVar7 = strlen((char *)local_b0);
  FUN_0307ccd0(&local_b8,local_b0,sVar7);
  FUN_0307b158(*param_1,&local_b8);
  FUN_0307c7fc(&local_b8,0,*(undefined8 *)(local_b8 + -0x18),0);
  sprintf((char *)local_b0,"Compressed:\t %d \n",(ulong)*(byte *)(param_2 + 9));
  sVar7 = strlen((char *)local_b0);
  FUN_0307ccd0(&local_b8,local_b0,sVar7);
  FUN_0307b158(*param_1,&local_b8);
  FUN_0307c7fc(&local_b8,0,*(undefined8 *)(local_b8 + -0x18),0);
                    /* try { // try from 02bde254 to 02cde283 has its CatchHandler @ 02bde7a0 */
  sprintf((char *)local_b0,"Encrypted:\t %d \n",(ulong)*(byte *)(param_2 + 10));
  sVar7 = strlen((char *)local_b0);
  FUN_0307ccd0(&local_b8,local_b0,sVar7);
  FUN_0307b158(*param_1,&local_b8);
                    /* try { // try from 02bde290 to 02cde297 has its CatchHandler @ 02bde7a4 */
  FUN_0307c7fc(&local_b8,0,*(undefined8 *)(local_b8 + -0x18),0);
  sprintf((char *)local_b0,"BlueBoxed:\t %d \n",(ulong)*(byte *)(param_2 + 0xb));
  sVar7 = strlen((char *)local_b0);
  FUN_0307ccd0(&local_b8,local_b0,sVar7);
  FUN_0307b158(*param_1,&local_b8);
                    /* try { // try from 02bde2cc to 02cde2fb has its CatchHandler @ 02bde6a8 */
  FUN_0307c7fc(&local_b8,0,*(undefined8 *)(local_b8 + -0x18),0);
  sprintf((char *)local_b0,"BigSized:\t %d \n",(ulong)*(byte *)(param_2 + 0xc));
  sVar7 = strlen((char *)local_b0);
  FUN_0307ccd0(&local_b8,local_b0,sVar7);
  FUN_0307b158(*param_1,&local_b8);
                    /* try { // try from 02bde324 to 02cde353 has its CatchHandler @ 02bde6a4 */
  FUN_0307b318(*param_1,"---------------------------------------------\n",0x2e);
  if (local_b8 + -0x18 != puVar5) {
                    /* try { // try from 02bde368 to 02cde373 has its CatchHandler @ 02bde724 */
    piVar8 = (int *)(local_b8 + -8);
    if (PTR_pthread_create_03bd6b78 == (undefined *)0x0) {
      iVar9 = *piVar8;
      *piVar8 = iVar9 + -1;
    }
    else {
      do {
        iVar9 = *piVar8;
                    /* try { // try from 02bde380 to 02cde38b has its CatchHandler @ 02bde6ac */
        cVar2 = '\x01';
        bVar3 = (bool)ExclusiveMonitorPass(piVar8,0x10);
        if (bVar3) {
          *piVar8 = iVar9 + -1;
          cVar2 = ExclusiveMonitorsStatus();
        }
      } while (cVar2 != '\0');
    }
    if (iVar9 < 1) {
      _ZdlPv(local_b8 + -0x18);
    }
  }
  if (*(long *)(lVar4 + 0x28) != local_48) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
                    /* try { // try from 02bde358 to 02cde363 has its CatchHandler @ 02bde78c */
  return;
}



// matched functions: 202 | thunk-resolved: 28
