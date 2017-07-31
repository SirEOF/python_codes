# coding=utf-8

import copy
import warnings

import time
from netdicom import StorageSOPClass

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=UserWarning)
    from dicom.UID import UID

import netdicom
import netdicom.ACSEprovider
import netdicom.SOPclass
import netdicom.applicationentity
import netdicom.DIMSEprovider
from netdicom.DULprovider import DULServiceProvider, MaximumLengthParameters, AsynchronousOperationsWindowSubItem, \
    SCP_SCU_RoleSelectionParameters
from netdicom.SOPclass import *


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


class XRayImageStorageSOPClass(StorageSOPClass):
    UID = "1.2.840.10008.5.1.4.1.1.1.1"


def run(self):
    self.ACSE = netdicom.ACSEprovider.ACSEServiceProvider(self.DUL)
    self.DIMSE = netdicom.DIMSEprovider.DIMSEServiceProvider(self.DUL)
    if self.Mode == 'Acceptor':
        self.ACSE.Accept(self.ClientSocket,
                         self.AE.AcceptablePresentationContexts)
        # call back
        self.AE.OnAssociateRequest(self)
        # build list of SOPClasses supported
        self.SOPClassesAsSCP = []
        for ss in self.ACSE.AcceptedPresentationContexts:
            self.SOPClassesAsSCP.append((ss[0], \
                                         netdicom.SOPclass.UID2SOPClass(ss[1]), ss[2]))

    else:  # Requestor mode
        # build role extended negociation
        ext = []
        for ii in self.AE.AcceptablePresentationContexts:
            tmp = SCP_SCU_RoleSelectionParameters()
            tmp.SOPClassUID = ii[0]
            tmp.SCURole = 0
            tmp.SCPRole = 1
            ext.append(tmp)

        ans = self.ACSE.Request(self.AE.LocalAE, self.RemoteAE,
                                self.AE.MaxPDULength,
                                self.AE.PresentationContextDefinitionList, \
                                userspdu=ext)
        if ans:
            # call back
            if 'OnAssociateResponse' in self.AE.__dict__:
                self.AE.OnAssociateResponse(ans)
        else:
            self.AssociationRefused = True
            self.DUL.Kill()
            return
        self.SOPClassesAsSCU = []
        for ss in self.ACSE.AcceptedPresentationContexts:
            self.SOPClassesAsSCU.append((ss[0],
                                         netdicom.SOPclass.UID2SOPClass(ss[1]), ss[2]))

    self.AssociationEstablished = True

    # association established. Listening on local and remote interfaces
    while not self._Kill:
        time.sleep(0.001)
        # look for incoming DIMSE message
        if self.Mode == 'Acceptor':
            dimsemsg, pcid = self.DIMSE.Receive(Wait=False, Timeout=None)
            if dimsemsg:
                # dimse message received
                uid = dimsemsg.AffectedSOPClassUID
                obj = netdicom.SOPclass.UID2SOPClass(uid.value)()
                try:
                    obj.pcid, obj.sopclass, obj.transfersyntax = \
                        [x for x in self.SOPClassesAsSCP \
                         if x[0] == pcid][0]
                except IndexError:
                    raise "SOP Class %s not supported as SCP" % uid
                obj.maxpdulength = self.ACSE.MaxPDULength
                obj.DIMSE = self.DIMSE
                obj.ACSE = self.ACSE
                obj.AE = self.AE

                # run SCP
                obj.SCP(dimsemsg)

            # check for release request
            if self.ACSE.CheckRelease():
                self.Kill()

            # check for abort
            if self.ACSE.CheckAbort():
                self.Kill()


def monkey_patch_netdicom():
    """
    修正:
        1. pynetdicom不能正确返回a_association_request请求的问题
        2. AsynchronousOperationsWindowSubItem不能作为子元素的问题
    """
    netdicom.ACSEprovider.ACSEServiceProvider.Accept = Accept
    AsynchronousOperationsWindowSubItem.ToSubItem = ToSubItem
    netdicom.applicationentity.Association.run = run
    netdicom.SOPclass.d.append('XRayImageStorageSOPClass')
    netdicom.SOPclass.XRayImageStorageSOPClass = XRayImageStorageSOPClass
