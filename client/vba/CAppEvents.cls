VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "CAppEvents"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
'=== Class Module: CAppEvents ===
Option Explicit

Public WithEvents PPTEvent As Application
Attribute PPTEvent.VB_VarHelpID = -1

' ===================================
' Event: SlideShowBegin
' FIX: Fires when the slideshow starts (i.e., when the first slide is shown).
' ===================================
Private Sub PPTEvent_SlideShowBegin(ByVal Wn As SlideShowWindow)
    On Error GoTo EH

    Dim currentNotes As String
    
    ' Get the slide object for the currently displayed slide (the first one)
    currentNotes = modHttpNotes.GetNotesText(Wn.View.Slide)

    Debug.Print "SlideShowBegin fired. Current position: " & (Wn.View.CurrentShowPosition)

    If Len(Trim$(currentNotes)) = 0 Then
        Debug.Print "Notes: (none)"
    Else
        Debug.Print "Notes:"
        Debug.Print currentNotes
        ' Call into the standard module to send the HTTP request
        modHttpNotes.SetWelcome currentNotes
    End If

    Exit Sub
EH:
    Debug.Print "? PPTEvent_SlideShowBegin error: "; Err.Number; " - "; Err.Description
End Sub


' ===================================
' Event: SlideShowNextSlide
' Fires when moving to the 2nd slide and every slide thereafter.
' ===================================
Private Sub PPTEvent_SlideShowNextSlide(ByVal Wn As SlideShowWindow)
    On Error GoTo EH

    Dim currentNotes As String
    currentNotes = modHttpNotes.GetNotesText(Wn.View.Slide)

    Debug.Print "SlideShowNextSlide fired. Current position: " & (Wn.View.CurrentShowPosition)

    If Len(Trim$(currentNotes)) = 0 Then
        Debug.Print "Notes: (none)"
    Else
        Debug.Print "Notes:"
        Debug.Print currentNotes
        ' Call into the standard module to send the HTTP request
        modHttpNotes.SetWelcome currentNotes
    End If

    Exit Sub
EH:
    Debug.Print "? PPTEvent_SlideShowNextSlide error: "; Err.Number; " - "; Err.Description
End Sub
