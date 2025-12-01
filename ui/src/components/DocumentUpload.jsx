import React, { useState } from 'react'
import { Button, Paper, Stack, TextField, Typography } from '@mui/material'

export default function DocumentUpload({ onTextReady, onPatchedTextReady }) {
  const [text, setText] = useState('')
  const [patch, setPatch] = useState('')

  const handleFile = (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => {
      const value = e.target?.result || ''
      setText(value)
      onTextReady(value.toString())
    }
    reader.readAsText(file)
  }

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>New Document</Typography>
      <Stack spacing={2}>
        <TextField
          label="Copy/Paste document text"
          value={text}
          onChange={(e) => {
            setText(e.target.value)
            onTextReady(e.target.value)
          }}
          multiline
          minRows={5}
        />
        <Button variant="outlined" component="label">
          Open/Upload file
          <input type="file" hidden onChange={handleFile} accept=".txt,.rtf,.doc,.docx,.html,.md" />
        </Button>
        <TextField
          label="Patch text"
          value={patch}
          onChange={(e) => {
            setPatch(e.target.value)
            onPatchedTextReady(e.target.value)
          }}
          multiline
          minRows={4}
          helperText="Add a proposed patch to compare against the document"
        />
      </Stack>
    </Paper>
  )
}
