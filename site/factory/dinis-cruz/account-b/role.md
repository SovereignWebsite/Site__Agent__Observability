# observability.b: role

Traffic counts for every SovereignWebsite site, without cookies and without any third party seeing a visitor's IP address.

- A shared browser script (seed/shared/traffic.js, through factory.b) sends one encrypted note per page: site, page, time to the minute, time zone, language, visitor type (person, team, synthetic, crawler) and a random id that lasts only for the tab.
- Notes go to write-only append lanes on a private sgit vault on SG/Send, one lane set per site.
- A drain (a script, no model) runs twice a day, drops any note that fails validation, and publishes totals only: per site in the site's own repository and on its admin page, and across all sites on observability.agents.sovereignweb.site.
- Published: views and visits per day by type; pages and countries over 28 days for people only; nothing under 5.
- Reviewed by security.b (review 003, pass with changes, all applied).
