# Optional TLS certificates

The current IP-only production configuration listens on HTTP port 80 and does
not mount this directory.

When a domain is assigned, add an HTTPS server block, mount `fullchain.pem` and
`privkey.pem`, then enable Django HTTPS redirect and secure cookies. Certificate
files are ignored by Git.
