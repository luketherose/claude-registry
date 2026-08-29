# Worked example

## Example

**Input:** `COMPONENT_NAME = "PolicyListView"`, Django template + view code injected,
Angular architecture spec provided.

**Output excerpt:**

```typescript
// policy-list.component.ts
@Component({
  selector: 'app-policy-list',
  templateUrl: './policy-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PolicyListComponent implements OnInit {
  private readonly policyService = inject(PolicyApiService);
  policies$: Observable<Policy[]>;

  ngOnInit(): void {
    this.policies$ = this.policyService.getAll().pipe(
      takeUntilDestroyed(this.destroyRef)
    );
  }
}
```

**Business rules preserved:** BR-01 (active filter default), BR-02 (pagination 20/page).
**Migration notes:** Django template loops → *ngFor with async pipe. No state management library needed.
```

---
