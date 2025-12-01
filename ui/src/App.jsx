import React, { useEffect, useMemo, useState } from 'react'
import { Container, CssBaseline, Grid, Paper, Stack, Tab, Tabs, TextField, Typography, Button } from '@mui/material'
import DocumentUpload from './components/DocumentUpload'
import DiffViewer from './components/DiffViewer'
import VotePanel from './components/VotePanel'

const localToken = () => localStorage.getItem('draft_hub_token') || ''

export default function App() {
  const [token, setToken] = useState(localToken())
  const [documentText, setDocumentText] = useState('')
  const [patchedText, setPatchedText] = useState('')
  const [tab, setTab] = useState(0)
  const [credentials, setCredentials] = useState({ username: '', password: '' })

  useEffect(() => {
    localStorage.setItem('draft_hub_token', token)
  }, [token])

  const diff = useMemo(() => ({
    document_text: documentText,
    patched_text: patchedText || documentText,
  }), [documentText, patchedText])

  const handleLogin = () => {
    if (!credentials.username || !credentials.password) return
    // In a real app this would call /auth/login; here we keep the UI responsive.
    setToken(btoa(`${credentials.username}:${credentials.password}`))
  }

  const handleLogout = () => {
    setToken('')
    localStorage.removeItem('draft_hub_token')
  }

  return (
    <React.Fragment>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h3" gutterBottom>Draft Hub</Typography>
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField label="Username" value={credentials.username} onChange={(e) => setCredentials({ ...credentials, username: e.target.value })} size="small" />
            <TextField label="Password" type="password" value={credentials.password} onChange={(e) => setCredentials({ ...credentials, password: e.target.value })} size="small" />
            <Button variant="contained" onClick={handleLogin}>Login</Button>
            <Button variant="text" onClick={handleLogout}>Logout</Button>
            <Typography variant="body2" color={token ? 'success.main' : 'text.secondary'}>
              {token ? 'JWT saved to local storage' : 'Not authenticated'}
            </Typography>
          </Stack>
        </Paper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <DocumentUpload
              onTextReady={(text) => setDocumentText(text)}
              onPatchedTextReady={(text) => setPatchedText(text)}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Tabs value={tab} onChange={(_, value) => setTab(value)}>
                <Tab label="Current Document" />
                <Tab label="Patch" />
                <Tab label="Diff" />
              </Tabs>
              {tab === 0 && (
                <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', mt: 2 }}>
                  {documentText || 'Paste or upload a document to get started.'}
                </Typography>
              )}
              {tab === 1 && (
                <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', mt: 2 }}>
                  {patchedText || 'Create a patch to see how it compares.'}
                </Typography>
              )}
              {tab === 2 && (
                <DiffViewer baseText={diff.document_text} targetText={diff.patched_text} />
              )}
            </Paper>
          </Grid>
        </Grid>

        <Paper variant="outlined" sx={{ p: 2, mt: 3 }}>
          <VotePanel approvals={2} rejections={1} minimumVotes={5} />
        </Paper>
      </Container>
    </React.Fragment>
  )
}
