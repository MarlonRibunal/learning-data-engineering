def retention_curve(cohort, activity):
    cohort = set(cohort)
    return {
        day: len(cohort & set(users))
        for day, users in sorted(activity.items())
    }
