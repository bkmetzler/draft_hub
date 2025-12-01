import React from 'react'
import { LinearProgress, Stack, Typography } from '@mui/material'

export default function VotePanel({ approvals, rejections, minimumVotes }) {
  const total = approvals + rejections
  const approvalPct = total ? Math.round((approvals / total) * 100) : 0
  const remaining = Math.max(minimumVotes - total, 0)

  return (
    <Stack spacing={1}>
      <Typography variant="h6">Voting</Typography>
      <Typography variant="body2">{approvals} approve / {rejections} reject (min {minimumVotes} votes)</Typography>
      <LinearProgress variant="determinate" value={approvalPct} color={approvalPct >= 50 ? 'success' : 'error'} />
      <Typography variant="body2">
        {remaining ? `${remaining} more vote(s) until the minimum is met` : 'Minimum vote requirement satisfied'}
      </Typography>
    </Stack>
  )
}
