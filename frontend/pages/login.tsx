import { Component, MouseEvent } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import isEmpty from 'lodash/isEmpty';

import Head from 'next/head';
import Link from 'next/link';
import { withRouter, NextRouter } from 'next/router';

import { LeftArrowIcon, LoadingView, LoginForm } from '@/components';
import { AppState, IBreadcrumbListItem } from '@/types';


class Login extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.handleBack = this.handleBack.bind(this);
    this.state = { email_token: '' };
  }

  handleBack(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.props.router.push('/');
  }

  componentDidMount() {
    const { router } = this.props;

    if (!isEmpty(router.query)) {
      const { email_token } = router.query;
      if (email_token && typeof email_token === 'string') {
        this.setState({ email_token });
      }
    }
  }

  componentDidUpdate(prevProps: Props) {
    const { router, user } = this.props;

    if (router.query !== prevProps.router.query) {
      const { email_token } = router.query;
      if (email_token && typeof email_token === 'string') {
        return this.setState({ email_token });
      }
    }

    if (user) {
      const { email_token } = this.state;
      // If coming from email verification page
      if (email_token && typeof email_token === 'string') {
        // Redirect back to email verification page while logged in w/ params
        router.replace(`/verify_email?token=${email_token}`);
      } else {
        // Otherwise redirect to dashboard
        router.replace('/dashboard');
      }
    }
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
        name: "Login",
        item: "https://simplepasswords.app/login"
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
          <title>Login - SimplePasswords</title>
          <script type="application/ld+json">{breadcrumb}</script>
        </Head>
        <main className='Page Page--login'>
          <div className='LeftArrowIcon-container'>
            <LeftArrowIcon
              onClick={this.handleBack}
              src='/left-arrow-wh.png'
              type='button'
              title='Back to home'
            />
          </div>
          <LoginForm />
          <span className='LoginLink LoginLink--login'>
            Stay on same page?&nbsp;
            <Link href='/login'>
              <a className='LoginLink-link'>Log in</a>
            </Link>
          </span>
          <div className='Footer Footer--login'>
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

interface State {
  email_token: string;
}

export default withRouter(connector(Login));