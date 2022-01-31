import { Component, MouseEvent } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import Head from 'next/head';
import Link from 'next/link';
import { withRouter, NextRouter } from 'next/router';

import { LeftArrowIcon, LoadingView, RegisterForm } from '@/components';
import { AppState, IBreadcrumbListItem } from '@/types';


class Register extends Component<Props> {
  constructor(props: Props) {
    super(props);
    this.handleBack = this.handleBack.bind(this);
  }

  handleBack(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.props.router.push('/');
  };

  componentDidUpdate(prevProps: Props) {
    if (this.props.user) this.props.router.replace('/dashboard');
  }

  render() {
    const breadcrumbList: IBreadcrumbListItem[] = [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: "https://simplepasswords.app"
      },
      {
        "@type": "ListItem",
        position: 2,
        name: "Register",
        item: "https://simplepasswords.app/register"
      }
    ];

    const breadcrumb = JSON.stringify({
      "@context": "https://schema.org/",
      "@type": "BreadcrumbList",
      "itemListElement": breadcrumbList
    });

    return !!this.props.user ? <LoadingView /> : (
      <>
        <Head>
          <title>Register - SimplePasswords</title>
          <link rel="canonical" href="https://simplepasswords.app/login" />
          <script type="application/ld+json">{breadcrumb}</script>
        </Head>
        <main className='Page Page--register'>
          <div className='LeftArrowIcon-container'>
            <LeftArrowIcon
              onClick={this.handleBack}
              src='/left-arrow-wh.png'
              type='button'
              title='Back to home'
            />
          </div>
          <h2>Register</h2>
          <RegisterForm />
          <span className='RegisterLink RegisterLink--login'>
            Already have an account?&nbsp;
            <Link href='/login'>
              <a className='RegisterLink-link'>Log in</a>
            </Link>
          </span>
          <span className='RegisterLink RegisterLink--register'>
            Stay on same page?&nbsp;
            <Link href='/register'>
              <a className='RegisterLink-link'>Sign up</a>
            </Link>
          </span>
          <div className='Footer Footer--register'>
            <div className='FooterLinks'>
              <span>&copy; 2022</span>
              &nbsp;&nbsp;&bull;&nbsp;&nbsp;
              <Link href={{ pathname: '/privacy' }}>
                <a className='FooterLink FooterLink--privacy'>Privacy Policy</a>
              </Link>
              &nbsp;&nbsp;&bull;&nbsp;&nbsp;
              <Link href={{ pathname: '/terms' }}>
                <a className='FooterLink FooterLink--terms'>Terms and Conditions</a>
              </Link>
            </div>
          </div>
        </main>
      </>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  user: state.user.user,
});

const connector = connect(mapStateToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  router: NextRouter;
}

export default withRouter(connector(Register));