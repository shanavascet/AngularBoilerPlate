import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { Web1QueryBuilderComponent } from './components/web1-query-builder/web1-query-builder.component';
import { CampaignSegmentationComponent } from './components/campaign-segmentation/campaign-segmentation.component';
import { LoanExclusionComponent } from './components/loan-exclusion/loan-exclusion.component';
import { ReleaseNotesComponent } from './components/release-notes/release-notes.component';
import { ContactUsComponent } from './components/contact-us/contact-us.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'web1-query-builder', component: Web1QueryBuilderComponent },
  { path: 'campaign-segmentation', component: CampaignSegmentationComponent },
  { path: 'loan-exclusion', component: LoanExclusionComponent },
  { path: 'release-notes', component: ReleaseNotesComponent },
  { path: 'contact-us', component: ContactUsComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
