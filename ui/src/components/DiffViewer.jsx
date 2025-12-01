import React, { useMemo } from 'react'
import { Paper, Stack, Typography } from '@mui/material'
import { diffWords } from 'diff'

const styles = {
  added: { backgroundColor: '#e6ffed' },
  removed: { backgroundColor: '#ffe6e6', textDecoration: 'line-through' },
}

export default function DiffViewer({ baseText, targetText }) {
  const parts = useMemo(() => diffWords(baseText || '', targetText || ''), [baseText, targetText])

  return (
    <Paper variant="outlined" sx={{ p: 2, mt: 2, maxHeight: 400, overflow: 'auto' }}>
      <Typography variant="subtitle1" gutterBottom>Diff preview</Typography>
      <Stack direction="row" flexWrap="wrap" spacing={0.5} sx={{ fontFamily: 'monospace' }}>
        {parts.map((part, index) => (
          <Typography
            component="span"
            key={`${part.value}-${index}`}
            sx={part.added ? styles.added : part.removed ? styles.removed : {}}
          >
            {part.value}
          </Typography>
        ))}
      </Stack>
    </Paper>
  )
}
