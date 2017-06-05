# coding=utf-8

import copy
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=UserWarning)
    from dicom.UID import UID

import netdicom
import netdicom.ACSEprovider
from netdicom.DULprovider import DULServiceProvider, MaximumLengthParameters, AsynchronousOperationsWindowSubItem


def Accept(self, client_socket=None, AcceptablePresentationContexts=None, Wait=True):
    """Waits for an association request from a remote AE. Upon reception of the request
    sends association response based on AcceptablePresentationContexts"""
    if self.DUL is None:
        self.DUL = DULServiceProvider(Socket=client_socket)
    ass = self.DUL.Receive(Wait=True)
    if ass is None:
        return None

    # 写死
    self.MaxPDULength = 16352

    # analyse proposed presentation contexts
    rsp = []
    self.AcceptedPresentationContexts = []
    acceptable_sop = [x[0] for x in AcceptablePresentationContexts]
    ok = False
    for ii in ass.PresentationContextDefinitionList:
        pcid = ii[0]
        proposed_sop = ii[1]
        proposed_ts = ii[2]
        if proposed_sop in acceptable_sop:
            acceptable_ts = [x[1] for x in AcceptablePresentationContexts if x[0] == proposed_sop][0]
            for ts in proposed_ts:
                ok = False
                if ts in acceptable_ts:
                    # accept sop class and ts
                    rsp.append((ii[0], 0, ts))
                    self.AcceptedPresentationContexts.append((ii[0], proposed_sop, UID(ts)))
                    ok = True
                    break
            if not ok:
                # Refuse sop class because of TS not supported
                rsp.append((ii[0], 1, ''))
        else:
            # Refuse sop class because of SOP class not supported
            rsp.append((ii[0], 1, ''))

    # Send response
    res = copy.copy(ass)
    res.CallingAETitle = ass.CalledAETitle
    res.CalledAETitle = ass.CallingAETitle
    res.PresentationContextDefinitionList = []
    res.PresentationContextDefinitionResultList = rsp
    res.Result = 0
    max_len = MaximumLengthParameters()
    max_len.MaximumLengthReceived = self.MaxPDULength
    async_oper_window = AsynchronousOperationsWindowSubItem()
    async_oper_window.MaximumNumberOperationsInvoked = 16
    async_oper_window.MaximumNumberOperationsPerformed = 16
    res.UserInformation = [max_len, async_oper_window]
    self.DUL.Send(res)
    return True


def ToSubItem(self):
    tmp = AsynchronousOperationsWindowSubItem()
    tmp.FromParams(self)
    return tmp


def monkey_patch_netdicom():
    """
    修正:
        1. pynetdicom不能正确返回a_association_request请求的问题
        2. AsynchronousOperationsWindowSubItem不能作为子元素的问题
    """
    netdicom.ACSEprovider.ACSEServiceProvider.Accept = Accept
    AsynchronousOperationsWindowSubItem.ToSubItem = ToSubItem
