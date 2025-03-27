import { Component } from '@angular/core';

interface SectionCard {
  title: string;
  description: string;
  route: string;
  icon: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  sections: SectionCard[] = [
    {
      title: 'Dashboard',
      description: 'View Segmentation Execution Status and Report',
      route: '/dashboard',
      icon: 'dashboard'
    },
    {
      title: 'Web1 Query Builder',
      description: 'Redirect to Web1 Report Query Builder',
      route: '/web1-query-builder',
      icon: 'build'
    },
    {
      title: 'Campaign Segmentation Management',
      description: 'Validate Queries, Edit Segmentation and Treatment, and Schedule Campaign',
      route: '/campaign-segmentation',
      icon: 'campaign'
    },
    {
      title: 'Loan Exclusion',
      description: 'Exclude Individual Loans by Loan Number and Telephone Number or Upload Loan Exclusion File',
      route: '/loan-exclusion',
      icon: 'block'
    },
    {
      title: 'Release Notes',
      description: 'Release Notes lists application adjustments in each release.',
      route: '/release-notes',
      icon: 'notes'
    },
    {
      title: 'Contact Us',
      description: 'Contact Information',
      route: '/contact-us',
      icon: 'contact_support'
    }
  ];
}
