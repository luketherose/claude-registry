# TODOs are not optional: be aggressive, not conservative

Defect repeatedly observed: the agent leaves Angular components empty (`// TBD`, `throw new Error('Not implemented')`, empty templates) when the source-to-Angular translation is uncertain. **This is forbidden.**

When the exact equivalent of a source-language construct in Angular is unknown:

1. Implement the most reasonable best-guess version, fully wired up (template, class, service call).
2. Add a `// TODO: [assumption made] - verify [what the human should check]` comment at the assumption point. The TODO must be specific enough that a reviewer understands the reservation in 5 seconds.
3. Continue with the rest of the file.

Examples:

```typescript
// ✅ Best-guess + explicit TODO
@Component({ selector: 'app-report-page', /* ... */ })
export class ReportPageComponent {
  private readonly reportService = inject(ReportService);

  // TODO: source uses a 'date_range' parameter that may be either a single date
  //       or a (from,to) tuple - assumed tuple here based on the CSV samples.
  //       Verify against the legacy Streamlit code's date_input usage.
  protected readonly range = signal<{ from: Date; to: Date }>({
    from: startOfMonth(new Date()),
    to: new Date()
  });
}

// ❌ Conservative stub — forbidden
@Component({ selector: 'app-report-page', /* ... */ })
export class ReportPageComponent {
  // TBD: date range handling
  ngOnInit() { throw new Error('Not implemented'); }
}
```
