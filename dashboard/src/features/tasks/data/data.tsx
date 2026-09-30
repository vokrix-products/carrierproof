import {CircleCheckBig, Clock, TriangleAlert} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// PRODUCT_CUSTOMIZE: replace this list with the real statuses this product
// produces (must match exactly what the backend poller writes to
// records.status). Every status must declare a severity tier above. Default
// values below are generic placeholders only — do not ship as-is.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Ready', value: 'Ready', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Ready With Flags', value: 'Ready with flags', icon: Clock, severity: 'warning' as Severity },
  { label: 'Action Required', value: 'Action required', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Blocked', value: 'Blocked', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Expired', value: 'Expired', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Incomplete', value: 'Incomplete', icon: Clock, severity: 'warning' as Severity },
  { label: 'Missing', value: 'Missing', icon: Clock, severity: 'warning' as Severity },
  { label: 'Uploaded', value: 'Uploaded', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Parsing', value: 'Parsing', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Extracted', value: 'Extracted', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Needs Review', value: 'Needs review', icon: Clock, severity: 'warning' as Severity },
  { label: 'Invalid Format', value: 'Invalid format', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unreadable', value: 'Unreadable', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Duplicate', value: 'Duplicate', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Expiring Soon Within 30 Days', value: 'Expiring soon within 30 days', icon: Clock, severity: 'warning' as Severity },
  { label: 'Valid', value: 'Valid', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Insufficient Coverage', value: 'Insufficient coverage', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Mismatch', value: 'Mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Not Found', value: 'Not found', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Flagged', value: 'Flagged', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unverified', value: 'Unverified', icon: Clock, severity: 'warning' as Severity },
  { label: 'Active', value: 'Active', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Inactive', value: 'Inactive', icon: Clock, severity: 'warning' as Severity },
  { label: 'Pending', value: 'Pending', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Revoked', value: 'Revoked', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Out Of Service', value: 'Out of service', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Mc/Dot Mismatch', value: 'MC/DOT mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Below Minimum', value: 'Below minimum', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Missing Required Coverage', value: 'Missing required coverage', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Additional Insured Missing', value: 'Additional insured missing', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Waiver Of Subrogation Missing', value: 'Waiver of subrogation missing', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Certificate Holder Mismatch', value: 'Certificate holder mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Cargo Limit Insufficient', value: 'Cargo limit insufficient', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Tin Mismatch', value: 'TIN mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Name Mismatch', value: 'Name mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Address Mismatch', value: 'Address mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Entity Type Mismatch', value: 'Entity type mismatch', icon: TriangleAlert, severity: 'critical' as Severity },
]
// __STATUSES_BLOCK_END__
